import math
import sys
from itertools import accumulate
import numpy as np
import datetime

from covid_19.manipulation import create_lagged_values_differences, recreate_lagged_values
from covid_19.pandasutils import filter_series

from scipy.optimize import minimize


def calculate_probabilities(delta_parameters):
    alphas = list(map(lambda x: safe_exp(x), delta_parameters))
    sum_alphas = list(accumulate(alphas))
    intermediate = list(map(lambda x: 1.0 - safe_exp(-x), sum_alphas))

    probabilities = [intermediate[0]]
    for i in range(1, len(alphas)):
        probability = intermediate[i] - intermediate[i - 1]
        probabilities.append(probability)

    probabilities.append(1.0 - sum(probabilities))
    return probabilities


def correct_daily_increments(total_reported_numbers, daily_increments, maximum_lag):
    number_of_days = len(total_reported_numbers)
    skip_first = max(number_of_days - maximum_lag, 0)
    corrected_daily_increments = np.full((number_of_days, maximum_lag + 1), np.nan)

    for i in range(number_of_days):
        for j in range(maximum_lag):
            corrected_daily_increments[i, j] = daily_increments[i, j]

        if i < skip_first:
            corrected_daily_increments[i, maximum_lag] = total_reported_numbers[i] - sum(daily_increments[i, 0:maximum_lag])

    return corrected_daily_increments


def calculate_log_likelihood_with_probability_parameters(total_reported_numbers, daily_increments, probabilities, beta=0.0):
    cumulative_probabilities = list(accumulate(probabilities))

    number_of_days = len(total_reported_numbers)
    maximum_lag = len(probabilities) - 1
    skip_first = max(number_of_days - maximum_lag, 0)

    def safe_log(p):
        if p > 0.0:
            return math.log(p)
        return -30.0

    log_probabilities = list(map(lambda x: safe_log(x), probabilities))

    log_likelihood = 0.0
    j = 2
    for i in range(skip_first, number_of_days):
        weight = math.exp(-beta * (number_of_days - 1 - i))
        log_likelihood -= weight * (total_reported_numbers[i] * safe_log(cumulative_probabilities[-j]))
        j = j + 1

    for i in range(number_of_days):
        weight = math.exp(-beta * (number_of_days - 1 - i))
        for d in range(min(number_of_days - i, maximum_lag + 1)):
            log_likelihood += weight * (daily_increments[i, d] * log_probabilities[d])

    return log_likelihood


def calculate_log_likelihood(total_reported_numbers, daily_increments, delta_parameters, beta=0.0):
    probabilities = calculate_probabilities(delta_parameters)
    return calculate_log_likelihood_with_probability_parameters(total_reported_numbers, daily_increments, probabilities, beta)


def calculate_log_likelihood_jacobian_probabilities(total_reported_numbers, daily_increments, probabilities, beta=0.0):
    cumulative_probabilities = list(accumulate(probabilities))
    number_of_days = len(total_reported_numbers)
    maximum_lag = len(probabilities) - 1
    skip_first = max(number_of_days - maximum_lag, 0)

    def safe_probability(p):
        if p > 0.0:
            return p
        return math.exp(-30.0)

    safe_probabilities = list(map(safe_probability, probabilities))

    jacobian_probabilities = [0.0] * len(probabilities)

    j = 2
    for i in range(skip_first, number_of_days):
        weight = math.exp(-beta * (number_of_days - 1 - i))
        tmp = weight * total_reported_numbers[i]
        if abs(tmp) > sys.float_info.epsilon:
            jacobian_contribution = tmp / safe_probability(cumulative_probabilities[-j])
            for k in range(maximum_lag - (i - skip_first)):
                jacobian_probabilities[k] -= jacobian_contribution
        j = j + 1

    for i in range(number_of_days):
        weight = math.exp(-beta * (number_of_days - 1 - i))
        for d in range(min(number_of_days - i, maximum_lag + 1)):
            tmp = weight * daily_increments[i, d]
            if abs(tmp) > sys.float_info.epsilon:
                jacobian_probabilities[d] += tmp / safe_probabilities[d]

    return jacobian_probabilities


def calculate_log_likelihood_jacobian_probabilities_without_last(total_reported_numbers, daily_increments, probabilities, beta=0.0):
    jacobian = calculate_log_likelihood_jacobian_probabilities(total_reported_numbers, daily_increments, probabilities, beta)
    jacobian_remapped = [0.0] * (len(jacobian) - 1)

    for i in range(len(jacobian) - 1):
        jacobian_remapped[i] = jacobian[i] - jacobian[-1]

    return jacobian_remapped


def safe_exp(x):
    if x > 13.81551056:
        return 1e06
    return math.exp(x)


def calculate_log_likelihood_jacobian(total_reported_numbers, daily_increments, delta_parameters, beta=0.0):
    probabilities = calculate_probabilities(delta_parameters)
    jacobian_probabilities = calculate_log_likelihood_jacobian_probabilities_without_last(total_reported_numbers, daily_increments, probabilities, beta)

    alpha_parameters = list(map(lambda x: safe_exp(x), delta_parameters))
    cumulative_alphas = list(accumulate(alpha_parameters))
    sum_exp_minus_cum_alphas = list(map(lambda x: safe_exp(-x), cumulative_alphas))

    jacobian_alpha = [0.0] * len(delta_parameters)
    for i in range(len(delta_parameters)):
        if i == 0:
            tmp = jacobian_probabilities[0] * (1.0 - probabilities[0])
        else:
            tmp = jacobian_probabilities[i] * sum_exp_minus_cum_alphas[i]

        for j in range(i + 1, len(delta_parameters)):
            tmp += jacobian_probabilities[j] * -probabilities[j]
        jacobian_alpha[i] = tmp

    jacobian_delta = [0.0] * len(delta_parameters)
    for i in range(len(delta_parameters)):
        jacobian_delta[i] = jacobian_alpha[i] * alpha_parameters[i]

    return jacobian_delta


def nowcast_cases_per_day(dt, get_lagged_values, get_cases_per_day_from_data_frame, data_repository, maximum_lag=np.inf, beta=0.0, method="L-BFGS-B", reporting_lag=0):
    df_lagged = get_lagged_values(maximum_lag)
    df_lagged = recreate_lagged_values(df_lagged, dt - datetime.timedelta(days=reporting_lag))
    first_date = df_lagged.index.unique().min()
    last_date = df_lagged.index.unique().max()

    cases_per_day = get_cases_per_day_from_data_frame(data_repository.get_dataset(dt))
    cases_per_day = filter_series(cases_per_day, first_date, last_date).to_numpy()

    if maximum_lag is np.inf:
        maximum_lag = len(df_lagged.columns)

    daily_increments = create_lagged_values_differences(df_lagged.to_numpy())
    daily_increments = correct_daily_increments(cases_per_day, daily_increments, maximum_lag)

    initial_delta_parameters = np.zeros(maximum_lag)

    def log_likelihood_function(x):
        return -calculate_log_likelihood(cases_per_day, daily_increments, x, beta=beta)

    def log_likelihood_jacobian(x):
        return -1.0 * np.array(calculate_log_likelihood_jacobian(cases_per_day, daily_increments, x, beta=beta))

    if method == "Powell":
        res = minimize(fun=log_likelihood_function, x0=initial_delta_parameters, method="Powell")
    elif method == "L-BFGS-B":
        res = minimize(fun=log_likelihood_function, x0=initial_delta_parameters, jac=log_likelihood_jacobian, method="L-BFGS-B")
    else:
        raise Exception("Unknown minimisation method - {method}".format(method=method))

    if not res.success:
        if method != "Powell":
            # Use a more robust gradient-free minimisation method as a fallback
            return nowcast_cases_per_day(dt, get_lagged_values, get_cases_per_day_from_data_frame, data_repository, maximum_lag, beta, "Powell")
        raise Exception("Minimisation has failed on date {dt}".format(dt=dt.isoformat()))

    probabilities = calculate_probabilities(res.x)
    cumulative_probabilities = list(accumulate(probabilities))
    corrected_cases_per_day = []
    for i in range(len(cases_per_day)):
        p = cumulative_probabilities[min(len(cases_per_day) - i - 1, maximum_lag)]
        corrected_cases_per_day.append(cases_per_day[i] / p)

    return corrected_cases_per_day, probabilities

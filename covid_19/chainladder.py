import math
from itertools import accumulate
import numpy as np

from covid_19.manipulation import create_lagged_values_differences, recreate_lagged_values
from covid_19.pandasutils import filter_series

from scipy.optimize import minimize


def calculate_probabilities(delta_parameters):
    def safe_exp(x):
        if x > 13.81551056:
            return 1e06
        return math.exp(x)

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


def calculate_log_likelihood(total_reported_numbers, daily_increments, delta_parameters, beta=0.0):
    probabilities = calculate_probabilities(delta_parameters)
    cumulative_probabilities = list(accumulate(probabilities))
    number_of_days = len(total_reported_numbers)
    maximum_lag = len(delta_parameters)
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


def nowcast_cases_per_day(dt, get_lagged_values, get_cases_per_day_from_data_frame, data_repository, maximum_lag=np.inf, beta=0.0):
    df_lagged = get_lagged_values(maximum_lag)
    df_lagged = recreate_lagged_values(df_lagged, dt)
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

    res = minimize(fun=log_likelihood_function, x0=initial_delta_parameters, method="Powell")
    probabilities = calculate_probabilities(res.x)
    cumulative_probabilities = list(accumulate(probabilities))
    corrected_cases_per_day = []
    for i in range(len(cases_per_day)):
        p = cumulative_probabilities[min(len(cases_per_day) - i - 1, maximum_lag)]
        corrected_cases_per_day.append(cases_per_day[i] / p)

    return corrected_cases_per_day, probabilities

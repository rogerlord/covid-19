import math
from itertools import accumulate
import numpy as np


def calculate_probabilities(delta_parameters):
    alphas = list(map(lambda x: math.exp(x), delta_parameters))
    sum_alphas = list(accumulate(alphas))
    intermediate = list(map(lambda x: 1.0 - math.exp(-x), sum_alphas))

    probabilities = [intermediate[0]]
    for i in range(1, len(alphas)):
        probability = intermediate[i] - intermediate[i - 1]
        probabilities.append(probability)

    probabilities.append(1.0 - sum(probabilities))
    return probabilities


def correct_daily_increments(total_reported_numbers, daily_increments, maximum_lag):
    number_of_days = len(total_reported_numbers)
    skip_first = max(number_of_days - maximum_lag, 0)
    corrected_daily_increments = np.empty((number_of_days, maximum_lag + 1)) * np.nan

    for i in range(number_of_days):
        for j in range(maximum_lag):
            corrected_daily_increments[i, j] = daily_increments[i, j]

        if i < skip_first:
            corrected_daily_increments[i, maximum_lag] = total_reported_numbers[i] - sum(daily_increments[i, 0:maximum_lag])

    return corrected_daily_increments


def calculate_log_likelihood(total_reported_numbers, daily_increments, delta_parameters):
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
        log_likelihood -= total_reported_numbers[i] * safe_log(cumulative_probabilities[-j])
        j = j + 1

    for i in range(number_of_days):
        for d in range(min(number_of_days - i, maximum_lag + 1)):
            log_likelihood += daily_increments[i, d] * log_probabilities[d]

    return log_likelihood

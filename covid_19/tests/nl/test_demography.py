from covid_19.nl.demography import get_population_per_ggd_region


def test_get_population_per_ggd_region():
    population_per_ggd_region = get_population_per_ggd_region()
    assert population_per_ggd_region["GG0111"] == 585_866
    assert len(population_per_ggd_region) == 25

from policyengine_us.model_api import *


class marginal_tax_rate_computed(Variable):
    value_type = bool
    entity = Person
    label = "marginal tax rate computed"
    documentation = (
        "Whether marginal_tax_rate, marginal_tax_rate_including_health_benefits, "
        "federal_marginal_tax_rate, state_marginal_tax_rate and "
        "fica_marginal_tax_rate are simulated for this person. They are "
        "simulated only for adults whose adult_earnings_index (rank by market "
        "income within the household) is at most "
        "simulation.marginal_tax_rate_adults. Everyone else, including "
        "children with earnings, gets a zero that is a placeholder, not a "
        "simulated result. Filter on this flag before summarizing those "
        "variables across people. marginal_tax_rate_on_capital_gains ranks "
        "adults separately and is not covered by this flag."
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        adult_count = parameters(period).simulation.marginal_tax_rate_adults
        adult_earnings_index = person("adult_earnings_index", period)
        return (
            person("is_adult", period)
            & (adult_earnings_index >= 1)
            & (adult_earnings_index <= adult_count)
        )

from policyengine_us.model_api import *


class nd_liheap_countable_unearned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "North Dakota LIHEAP countable unearned income"
    reference = (
        "https://www.nd.gov/dhs/policymanuals/415/415_25_05_20_20.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_25_05_27_15.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_25_05_30.htm",
    )
    defined_for = StateCode.ND

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nd.dhs.liheap.income
        income = 0
        for source in p.unearned_sources:
            income = income + max_(person(source, period), 0)
        contributions = person("financial_assistance", period)
        # This input lacks regularity and education-conditioned support flags;
        # supplied amounts are treated as recurring, unconditional support.
        countable_contributions = where(
            contributions >= p.cash_contribution_threshold, contributions, 0
        )
        return income + countable_contributions

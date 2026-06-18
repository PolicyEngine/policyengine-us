from policyengine_us.model_api import *


class pa_nontaxable_retirement_distributions(Variable):
    value_type = float
    entity = Person
    label = "Retirement distributions taxable by US but not by PA"
    unit = USD
    documentation = (
        "US taxable non-employer retirement distributions excluded from PA "
        "AGI after Pennsylvania's qualifying retirement age."
    )
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/agencies/revenue/forms-and-publications/"
        "pa-personal-income-tax-guide/gross-compensation.html"
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.tax.income
        retired = person("age", period) >= p.retirement_age_threshold
        distributions = person("taxable_ira_distributions", period)
        return where(retired, distributions, 0)

from policyengine_us.model_api import *


class pa_uc_maximum_weeks(Variable):
    value_type = int
    entity = Person
    label = "Pennsylvania unemployment compensation maximum benefit weeks"
    unit = "week"
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=133",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        # § 404(c): maximum weeks of entitlement equals the number of credit
        # weeks during the base year, up to a maximum of twenty-six.
        credit_weeks = person("pa_uc_credit_weeks", period)
        p = parameters(period).gov.states.pa.dli.unemployment_compensation
        return min_(credit_weeks, p.maximum_weeks)

from policyengine_us.model_api import *


class nj_employer_workforce_fund_contribution(Variable):
    value_type = float
    entity = Person
    label = "New Jersey employer workforce fund contribution"
    documentation = (
        "Employer contribution to the New Jersey workforce development and "
        "supplemental workforce funds, on wages up to the unemployment "
        "insurance taxable wage base."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NJ
    reference = "https://www.nj.gov/labor/ea/employer-services/rate-info/"

    def formula(person, period, parameters):
        rate = person("nj_employer_workforce_fund_contribution_rate", period)
        return rate * person("nj_taxable_earnings_for_state_unemployment_tax", period)

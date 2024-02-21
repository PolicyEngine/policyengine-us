from policyengine_us.model_api import *


class ca_investment_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California investment interest deduction"
    unit = USD
    documentation = "https://www.ftb.ca.gov/forms/2021/2021-3526.pdf"
    definition_period = YEAR
    defined_for = StateCode.CA

from policyengine_us.model_api import *


class ca_itemized_deductions_pre_limitation(Variable):
    value_type = float
    entity = TaxUnit
    label = "California pre-limitation itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540-ca-instructions.html"
        "https://www.ftb.ca.gov/forms/2022/2022-540-ca-instructions.html"
    )
    defined_for = StateCode.CA

    adds = [
        "ca_investment_interest_deduction",
        "real_estate_taxes",
        "itemized_deductions_less_salt",
    ]

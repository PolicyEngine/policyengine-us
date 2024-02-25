from policyengine_us.model_api import *


class ca_pre_exemption_amti(Variable):
    value_type = float
    entity = TaxUnit
    label = "California pre-exemption alternative minimum taxable income"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-540-p.pdf"

    # Line 19
    adds = [
        "ca_amti_adjustments",
        "ca_taxable_income",
        "ca_itemized_deductions_pre_limitation",
    ]

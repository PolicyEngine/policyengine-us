from policyengine_us.model_api import *


class ny_itemized_deductions_max(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY uncapped itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/615"
    defined_for = StateCode.NY
    adds = [
        "itemized_deductions_less_salt",
        "real_estate_taxes",
        "ny_college_tuition_deduction",
    ]

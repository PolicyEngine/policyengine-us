from policyengine_us.model_api import *


class ny_itemized_deductions_incremental_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York itemized deductions incremental reduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/615"  # (f)
    defined_for = "ny_itemized_deductions_reduction_applies"

    adds = [
        "ny_itemized_deductions_higher_incremental_reduction",
        "ny_itemized_deductions_lower_incremental_reduction",
    ]

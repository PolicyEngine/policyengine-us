from policyengine_us.model_api import *


class ny_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/615"
    defined_for = StateCode.NY

    adds = ["ny_itemized_deductions_max"]
    subtracts = ["ny_itemized_deductions_reduction"]

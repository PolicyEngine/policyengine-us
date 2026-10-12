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
    # IT-196 applies two reductions in sequence: the pre-TCJA federal overall
    # limitation (Line 40, keyed on federal AGI, 26 U.S.C. 68 via NY Tax Law
    # 615 conformity) first, then NY's own higher-income adjustment (Line 46,
    # keyed on NY AGI per 615(f)/(g)). Both are modeled here as amounts
    # subtracted from ny_itemized_deductions_max.
    subtracts = [
        "ny_itemized_deductions_phase_out",
        "ny_itemized_deductions_reduction",
    ]

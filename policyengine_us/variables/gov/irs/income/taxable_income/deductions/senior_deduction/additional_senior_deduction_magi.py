from policyengine_us.model_api import *


class additional_senior_deduction_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Modified adjusted gross income for the senior deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/151#d_5_C",
        "https://www.congress.gov/119/bills/hr1/BILLS-119hr1enr.pdf#page=88",
        "https://www.irs.gov/pub/irs-pdf/f1040s1a.pdf#page=1",
    )
    # 26 U.S.C. 151(d)(5)(C)(iii)(II): adjusted gross income increased by
    # any amount excluded from gross income under section 911, 931, or 933.
    adds = ["agi_plus_section_911_931_933_exclusions"]

from policyengine_us.model_api import *


class sstb_w2_wages_from_qualified_business(Variable):
    value_type = float
    entity = Person
    label = "SSTB allocable W-2 wages"
    unit = USD
    documentation = (
        "Portion of w2_wages_from_qualified_business allocable to specified "
        "service trades or businesses for section 199A. Used to apply the "
        "W-2 wage limitation separately to SSTB and non-SSTB categories in "
        "mixed-business cases."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#b_2",
        "https://www.law.cornell.edu/uscode/text/26/199A#d_3",
        "https://www.irs.gov/pub/irs-pdf/f8995aa.pdf",
    )
    default_value = 0

from policyengine_us.model_api import *


class sstb_unadjusted_basis_qualified_property(Variable):
    value_type = float
    entity = Person
    label = "SSTB allocable UBIA of qualified property"
    unit = USD
    documentation = (
        "Portion of unadjusted_basis_qualified_property allocable to "
        "specified service trades or businesses for section 199A. Used to "
        "apply the UBIA limitation separately to SSTB and non-SSTB "
        "categories in mixed-business cases."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#b_2",
        "https://www.law.cornell.edu/uscode/text/26/199A#d_3",
        "https://www.irs.gov/pub/irs-pdf/f8995aa.pdf",
    )
    default_value = 0

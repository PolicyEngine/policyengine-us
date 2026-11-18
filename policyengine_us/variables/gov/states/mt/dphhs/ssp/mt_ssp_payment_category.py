from policyengine_us.model_api import *


class MTSSPPaymentCategory(Enum):
    ASSISTED_LIVING_OR_GROUP_OR_COMMUNITY_HOME = (
        "State-certified personal care, group or community home"
    )
    FOSTER_CARE = "State-certified child or adult foster care"
    TRANSITIONAL_LIVING = "State-certified transitional living services"
    CATEGORY_B_ASSISTED_LIVING = "Excluded category B assisted living facility"
    NONE = "No state-certified supplementary payment placement"


class mt_ssp_payment_category(Variable):
    value_type = Enum
    entity = Person
    label = "Montana SSP state-certified payment category"
    definition_period = MONTH
    possible_values = MTSSPPaymentCategory
    default_value = MTSSPPaymentCategory.NONE
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501415058#h1",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415010DEN",
        "https://mca.legmt.gov/bills/mca/title_0520/chapter_0010/part_0010/section_0040/0520-0010-0010-0040.html",
        "https://secure.ssa.gov/poms.nsf/lnx/0502005030#g",
        "https://secure.ssa.gov/poms.nsf/lnx/0500501154",
    )
    documentation = """
    A positive category requires Montana's placement certification, not just
    residence in a licensed facility. Category B assisted living is excluded
    (MCA 52-1-104(3)). Certified residents are in federal living arrangement A
    (SI DEN01415.010 B.6.b), so leave the household-of-another inputs unset for
    them; a resident of a Medicaid facility receives no supplement. A joint
    couple averages the two spouses' couple rates (SI 02005.030 G.1). Put
    spouses who no longer live in the same household, such as a certified-home
    resident whose spouse stays at home, in separate marital units from the
    month after they stop living together. Keep one marital unit for the month
    of entry.
    """

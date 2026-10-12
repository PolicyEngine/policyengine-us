from policyengine_us.model_api import *


class MTSSPPaymentCategory(Enum):
    NONE = "No state-certified supplementary payment placement"
    ASSISTED_LIVING_OR_GROUP_OR_COMMUNITY_HOME = (
        "State-certified personal care, group or community home"
    )
    FOSTER_CARE = "State-certified child or adult foster care"
    TRANSITIONAL_LIVING = "State-certified transitional living services"
    CATEGORY_B_ASSISTED_LIVING = "Excluded category B assisted living facility"


class mt_ssp_payment_category(Variable):
    value_type = Enum
    entity = Person
    label = "Montana SSP state-certified payment category"
    definition_period = MONTH
    possible_values = MTSSPPaymentCategory
    default_value = MTSSPPaymentCategory.NONE
    reference = (
        "https://secure.ssa.gov/poms.nsf/lnx/0501415010DEN",
        "https://mca.legmt.gov/bills/mca/title_0520/chapter_0010/part_0010/section_0040/0520-0010-0010-0040.html",
    )
    documentation = """
    A positive category requires Montana's placement certification, not just
    residence in a licensed facility. Category B assisted living is excluded.
    """

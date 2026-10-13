from policyengine_us.model_api import *


class ORSSPCategory(Enum):
    IN_HOME = "Approved SSI-only in-home services"
    COMMUNITY_CARE = "Approved licensed community care with an SSI spouse"
    DISABILITY_INTERIM = (
        "State disability determination while pursuing SSI through final appeal"
    )
    SSI_RESTORATION = "Leaving nursing care and pursuing full SSI restoration"
    VA_RESTORATION = "Leaving nursing care and pursuing full VA pension restoration"
    NATURALIZATION = "Qualified noncitizen pursuing naturalization after SSI time limit"
    SUSPENDED_SSI = (
        "Leaving a public institution and pursuing suspended SSI reinstatement"
    )
    SPOUSAL_DIVERSION = "Approved additional community-spouse diversion"
    ROOM_BOARD_ABSENCE = "Approved temporary absence with intent to return"
    ROOM_BOARD_INCAPACITY = (
        "Approved inaccessible-income case pending representative appointment"
    )
    INITIAL_ROOM_BOARD = "Approved initial placement room and board"
    NONE = "No approved OSIPM special need"


class or_ssp_category(Variable):
    value_type = Enum
    entity = Person
    label = "Oregon SSP approved special need category"
    definition_period = MONTH
    possible_values = ORSSPCategory
    default_value = ORSSPCategory.NONE
    reference = (
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-155-0575.pdf",
        # PDF pages 1-3
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-155-0630.pdf#page=1",
        # PDF pages 1-3
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-155-0700.pdf#page=1",
    )
    documentation = """
    Select only after OSIPM financial eligibility, placement/service authorization,
    lack of other resources to meet the need, and the category's procedural
    requirements are established. Includes approval of temporary-absence and
    incapacity extensions. Change to NONE when authorization or required
    pursuit of benefits ends. Specialized care eligibility is not inferred
    from ordinary Medicaid enrollment.
    """

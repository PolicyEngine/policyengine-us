from policyengine_us.model_api import *


class ms_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Mississippi LIHEAP eligible household size"
    documentation = (
        "Number of documented household members. Rule 6.3 B-C leave an "
        "undocumented member out of household size while still counting that "
        "member's income. Rule 6.1 B requires the applicant to be a U.S. citizen "
        "or legal permanent resident, and Rule 6.3 C refers to the other "
        "members' satisfactory immigration status without defining it, so "
        "citizens and the qualified noncitizens of 8 U.S.C. 1641 are counted as "
        "documented. The SPM unit approximates the household: live-in "
        "attendants, boarders and their separate energy arrangements are not "
        "identified."
    )
    defined_for = StateCode.MS
    reference = (
        # Rule 6.1 B (page 22) and Rule 6.3 A-C (page 23).
        "https://www.sos.ms.gov/adminsearch/ACCode/00000693c.pdf#page=22",
    )
    adds = ["is_citizen_or_legal_immigrant"]

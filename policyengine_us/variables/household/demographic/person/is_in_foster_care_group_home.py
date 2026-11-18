from policyengine_us.model_api import *


class is_in_foster_care_group_home(Variable):
    value_type = bool
    entity = Person
    label = "Person is currently in a qualifying foster care group home or short-term residential therapeutic program"
    documentation = (
        "Set this input to true for a foster youth placed in a qualifying "
        "group home or a short-term residential therapeutic program (STRTP). "
        "Set it to false for a foster youth placed in a foster family home, "
        "foster family agency home, transitional housing placement (THP+FC or "
        "THP-NMD), whole family foster home, resource family home or "
        "supervised independent living placement (SILP). On page 6 of All "
        "County Letters 15-58 and 16-57, the California Department of Social "
        "Services lists a group home infant supplement and a base amount for "
        "foster family homes, foster family agencies, THP+FC and SILPs. On "
        "PDF page 5 of All County Letter 26-44, the department lists an STRTP "
        "amount for the infant supplement and expectant parent payment. In "
        "the same table, it lists a base amount for foster family homes, "
        "foster family agencies, THP-NMD, whole family foster homes, resource "
        "families and SILPs."
    )
    definition_period = MONTH
    default_value = False
    reference = (
        "https://www.cdss.ca.gov/lettersnotices/EntRes/getinfo/acl/2015/15-58.pdf#page=6",
        "https://www.cdss.ca.gov/lettersnotices/EntRes/getinfo/acl/2016/16-57.pdf#page=6",
        "https://cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2026/26-44.pdf#page=5",
    )

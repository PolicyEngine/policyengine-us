from policyengine_us.model_api import *


class il_hfs_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois HFS immigration status eligible"
    documentation = (
        "Eligibility based on immigration status for Illinois HFS programs. "
        "Applicants must be a U.S. citizen or qualified immigrant for ongoing "
        "coverage under programs like Family Planning."
    )
    definition_period = YEAR
    reference = "https://www.dhs.state.il.us/page.aspx?item=146077"
    defined_for = StateCode.IL
    # Placeholder: defaults to True (assumes eligible)
    # TODO: Implement full immigration status check
    default_value = True

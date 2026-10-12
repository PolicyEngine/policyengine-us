from policyengine_us.model_api import *


class UTCCAPChildCountGroup(Enum):
    ONE = "One child"
    TWO = "Two children"
    THREE_PLUS = "More than two children"


class ut_ccap_child_count_group(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = UTCCAPChildCountGroup
    default_value = UTCCAPChildCountGroup.ONE
    definition_period = MONTH
    label = "Utah CCAP children receiving subsidy group"
    defined_for = StateCode.UT
    reference = (
        "https://jobs.utah.gov/Infosource/eligibilitymanual/Tables,_Appendicies,_and_Charts/Tables,_Appendicies,_and_Charts/Table_4_-_Child_Care_Income_Eligibility_and_Co-Payment.htm",
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-700-707",
    )

    def formula(spm_unit, period, parameters):
        # The Table 4 copayment columns are keyed by the number of children
        # receiving a subsidy; eligible children proxy the children in
        # subsidized care.
        eligible_children = add(spm_unit, period, ["ut_ccap_eligible_child"])
        return select(
            [eligible_children <= 1, eligible_children == 2],
            [UTCCAPChildCountGroup.ONE, UTCCAPChildCountGroup.TWO],
            default=UTCCAPChildCountGroup.THREE_PLUS,
        )

from policyengine_us.model_api import *


class co_ccap_has_verified_additional_care_needs(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    defined_for = StateCode.CO
    label = "Has verified additional care needs for Colorado CCCAP"
    documentation = (
        "Additional care needs documented by an individual health care plan, "
        "individual education plan, physician or professional statement, child "
        "welfare, or individualized family service plan under 8 CCR 1403-1 "
        "section 3.103. Court supervision alone does not establish this fact."
    )
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=2"

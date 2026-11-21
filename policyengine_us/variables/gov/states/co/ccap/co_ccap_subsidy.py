from policyengine_us.model_api import *


class co_ccap_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado Child Care Assistance Program"
    unit = USD
    definition_period = MONTH
    defined_for = "co_ccap_eligible"
    reference = (
        # 8 CCR 1403-1 3.103(UU), PDF page 9
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=9",
        # 3.111(F), PDF page 35
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=35",
        # 3.132(D) and (E), PDF page 126
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=126",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        # 8 CCR 1403-1 3.132(D) and (E) pay for the care of eligible children:
        # children under 13, and children under 19 who can't care for
        # themselves or who are under court supervision (3.103(UU), 3.111(F)).
        # A member outside those limits, such as a teenager, adds nothing.
        eligible_child = person("co_ccap_child_eligible", period)
        charge = add(
            person,
            period,
            ["pre_subsidy_childcare_expenses", "after_school_expenses"],
        )
        expenses = spm_unit.sum(charge * eligible_child)
        parent_fee = spm_unit("co_ccap_parent_fee", period)
        return max_(expenses - parent_fee, 0)

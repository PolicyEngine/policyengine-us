from policyengine_us.model_api import *


class co_ccap_reimbursement(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program reimbursement for the eligible children's care"
    defined_for = "co_ccap_eligible"
    reference = (
        # 8 CCR 1403-1 3.125(FFF), PDF page 101: the lesser of the provider's
        # private pay rate and the county reimbursement rate.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=101",
        # 3.130, PDF pages 118 and 119: the county reimbursement rates.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=118",
        # 3.132(D) and (E), PDF page 126: the children whose care CCCAP pays.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=126",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        eligible_child = person("co_ccap_child_eligible", period)
        charge = add(
            person,
            period,
            ["pre_subsidy_childcare_expenses", "after_school_expenses"],
        )
        county_rate = person("co_ccap_maximum_monthly_payment", period)
        reimbursable = min_(max_(charge, 0), county_rate)
        return spm_unit.sum(reimbursable * eligible_child)

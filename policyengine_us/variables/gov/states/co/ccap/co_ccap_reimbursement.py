from policyengine_us.model_api import *


class co_ccap_reimbursement(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program reimbursement for the eligible children's care"
    defined_for = "co_ccap_eligible"
    reference = (
        # 8 CCR 1403-1 3.125(FFF), 3.130 and 3.132(D) and (E), PDF pages 101,
        # 118-119, 126: the lesser of the provider's private pay rate and the
        # county reimbursement rate, the county rates, and the children whose
        # care CCCAP pays.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=101",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        eligible_child = person("co_ccap_child_eligible", period)
        charges = person("co_ccap_child_charges", period)
        county_rate = person("co_ccap_maximum_monthly_payment", period)
        reimbursable = min_(charges, county_rate)
        return spm_unit.sum(reimbursable * eligible_child)

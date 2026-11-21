from policyengine_us.model_api import *


class co_ccap_charges_above_rate(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program charges above the county rate"
    documentation = (
        "The eligible children's charges above the county reimbursement rate, "
        "which the provider may not collect from the family."
    )
    defined_for = "co_ccap_eligible"
    reference = (
        # 8 CCR 1403-1 3.128(T), PDF page 116: a provider may not charge a
        # CCCAP family more than the daily reimbursement rate in its fiscal
        # agreement.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=116",
    )

    def formula(spm_unit, period, parameters):
        # The county pays each eligible child's charges up to the county rate
        # (co_ccap_reimbursement), and the provider absorbs the rest. CDEC
        # lets a provider charge the family for care the county hasn't
        # authorized, but no input separates that care, so the model reads
        # every reported charge as authorized care.
        person = spm_unit.members
        eligible_child = person("co_ccap_child_eligible", period)
        charges = person("co_ccap_child_charges", period)
        county_rate = person("co_ccap_maximum_monthly_payment", period)
        return spm_unit.sum(max_(charges - county_rate, 0) * eligible_child)

from policyengine_us.model_api import *


class wa_wccc(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington Working Connections Child Care subsidy"
    unit = USD
    definition_period = MONTH
    defined_for = "wa_wccc_eligible"
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0190",
        "https://app.leg.wa.gov/wac/default.aspx?cite=110-15-0200",
    )

    def formula(spm_unit, period, parameters):
        copay = spm_unit("wa_wccc_copay", period)
        max_reimbursement = add(spm_unit, period, ["wa_wccc_max_monthly_reimbursement"])
        actual_expenses = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        uncapped = max_(actual_expenses - copay, 0)
        return min_(uncapped, max_reimbursement)

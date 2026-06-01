from policyengine_us.model_api import *


class az_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Arizona Child Care Assistance Program benefit"
    definition_period = MONTH
    defined_for = "az_ccap_eligible"
    reference = (
        "https://des.az.gov/sites/default/files/dl/CCA-1227A.pdf",
        "https://apps.azsos.gov/public_services/Title_06/6-05.pdf#page=40",
    )

    def formula(spm_unit, period):
        max_reimbursement = add(spm_unit, period, ["az_ccap_max_reimbursement"])
        childcare_expenses = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        copay = spm_unit("az_ccap_copay", period)
        return max_(min_(childcare_expenses, max_reimbursement) - copay, 0)

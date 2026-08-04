from policyengine_us.model_api import *


class nm_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "New Mexico CCAP benefit amount"
    definition_period = MONTH
    defined_for = "nm_ccap_eligible"
    reference = (
        "https://www.srca.nm.gov/parts/title08/08.015.0002.html",
        "https://www.nmececd.org/wp-content/uploads/2024/05/Cost-Model-Reimbursement-Rate-Flyer-English-and-Spanish-Revised-May-2024.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        # 8.15.2.13.C: ECECD pays providers the lesser of the reimbursement
        # rate and the provider's actual charge, less the family copayment.
        # Following the standard PolicyEngine childcare pattern (see RI CCAP),
        # the reimbursement is summed across eligible children and capped at
        # the family's actual pre-subsidy expenses at the SPM-unit level.
        max_reimbursement = add(spm_unit, period, ["nm_ccap_monthly_rate"])
        # spm_unit_pre_subsidy_childcare_expenses is annual; reading it with
        # the bare period auto-divides it to a monthly amount.
        actual_expenses = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        copay = spm_unit("nm_ccap_copay", period)
        return max_(min_(max_reimbursement, actual_expenses) - copay, 0)

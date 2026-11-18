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
        "https://www.srca.nm.gov/parts/title08/08.009.0003.html",
        # PDF pages 2, 13
        "https://prod-rf-lambda.rtssaas.com/PublicFiles/d89c47bd0d70402dba89b03a22bda6d1/b0e207a9-a1a3-412d-9660-0a6e925f6f25/8.9.3.pdf#page=2",
        "https://www.nmececd.org/wp-content/uploads/2024/05/Cost-Model-Reimbursement-Rate-Flyer-English-and-Spanish-Revised-May-2024.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        # 8.15.2.7.C(5) (8.9.3.7.C(5) from 2022-11-01; 8.9.3.7.C(8) and
        # 8.9.3.14.E from 2026-09-09): the department's payment to the provider
        # is reduced by the family copayment. Following the standard
        # PolicyEngine childcare pattern (see RI CCAP), the reimbursement is
        # summed across eligible children and capped at the family's actual
        # pre-subsidy expenses at the SPM-unit level.
        max_reimbursement = add(spm_unit, period, ["nm_ccap_monthly_rate"])
        # spm_unit_pre_subsidy_childcare_expenses is annual; reading it with
        # the bare period auto-divides it to a monthly amount.
        actual_expenses = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        copay = spm_unit("nm_ccap_copay", period)
        return max_(min_(max_reimbursement, actual_expenses) - copay, 0)

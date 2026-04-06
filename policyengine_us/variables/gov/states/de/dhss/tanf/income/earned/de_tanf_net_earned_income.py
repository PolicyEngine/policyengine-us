from policyengine_us.model_api import *


class de_tanf_net_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Delaware TANF net earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008",
        "https://dhss.delaware.gov/wp-content/uploads/sites/11/dss/pdf/detanfstateplan2017.pdf#page=6",
    )
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        # Per DSSM 4008 / State Plan Exhibit 1 Step 2 (Applicant Eligibility):
        # Gross earned - $90 work expense - childcare
        # NOTE: $30+1/3 disregard is NOT applied here - only in benefit calc
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        work_expense = spm_unit("de_tanf_earned_income_deduction", period)
        dependent_care = spm_unit("de_tanf_dependent_care_deduction", period)
        return max_(gross_earned - work_expense - dependent_care, 0)

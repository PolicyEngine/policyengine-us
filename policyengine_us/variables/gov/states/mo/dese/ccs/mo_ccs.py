from policyengine_us.model_api import *


class mo_ccs(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Missouri Child Care Subsidy benefit amount"
    definition_period = MONTH
    defined_for = "mo_ccs_eligible"
    reference = "https://www.law.cornell.edu/regulations/missouri/5-CSR-25-200-060"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dese.ccs
        # Reimbursement is paid per child at a daily rate for each day of care,
        # capped at the family's child care charges.
        person = spm_unit.members
        daily_benefit = person("mo_ccs_maximum_daily_benefit", period)
        days = person("childcare_attending_days_per_month", period.this_year)
        pre_subsidy_per_child = person("pre_subsidy_childcare_expenses", period)
        per_child_reimbursement = min_(daily_benefit * days, pre_subsidy_per_child)
        total_reimbursement = spm_unit.sum(per_child_reimbursement)
        copay = spm_unit("mo_ccs_copay", period)

        # Transitional Child Care families are funded at a reduced share of the
        # base rate remaining after the sliding fee is subtracted (5 CSR
        # 25-200.060(4)(C) Transitional Child Care and Manual 2010.045.00: DESE
        # funds the percentage "of the remaining state base rate"). Traditional
        # families are funded at the full rate, so the multiplier is 1 and the
        # order has no effect.
        adjusted_income = spm_unit("mo_ccs_adjusted_income", period)
        monthly_fpg = spm_unit("spm_unit_fpg", period)
        fpl_ratio = where(monthly_fpg > 0, adjusted_income / monthly_fpg, 0)
        funding_rate = p.transitional.funding_rate.calc(fpl_ratio)
        return funding_rate * max_(total_reimbursement - copay, 0)

from policyengine_us.model_api import *


class ks_ccap_family_share(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Kansas CCAP family share deduction"
    definition_period = MONTH
    defined_for = "ks_ccap_eligible"
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/Current/keesm7540.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Appendix/F-1MonthlyFamilyIncomeandFamilyShareDeductionSchedule.pdf",
        "https://content.dcf.ks.gov/ees/KEESM/Implem_Memo/2026_05_01_ccfpl_increase.html",
    )

    def formula(spm_unit, period, parameters):
        # KEESM 7541 / Appendix F-1: the family share deduction is set from the
        # family's monthly gross income relative to the FPL tiers for its size.
        # Families at or below 100% FPL owe $0; within each tier between 100%
        # and 185% FPL the deduction is 3% of the tier's lower bound, and above
        # 185% FPL it is 5% of the 185% FPL bound (DCF 2026-05-01 memo). KEESM
        # 7541 assesses the deduction only for income-eligible (non-TANF)
        # clients, so TANF recipients owe no family share. We don't model the
        # KEESM 2835 exceptions (e.g. child care to prevent abuse/neglect).
        p = parameters(period).gov.states.ks.dcf.ccap.family_share
        income = spm_unit("ks_ccap_countable_income", period)
        size = spm_unit("spm_unit_size", period.this_year)
        state_group = spm_unit.household("state_group_str", period.this_year)
        # CCAP requires a child, so the schedule starts at a family of 2;
        # families larger than the F-1 maximum use the largest column's values.
        capped_size = min_(size, p.max_family_size)
        # Monthly FPG for the (capped) size: Kansas is contiguous US.
        p_fpg = parameters(period).gov.hhs.fpg
        annual_fpg = p_fpg.first_person[state_group] + p_fpg.additional_person[
            state_group
        ] * (capped_size - 1)
        monthly_fpg = annual_fpg / MONTHS_IN_YEAR
        # The family's income tier follows the F-1 "Income Limit" column (FPL
        # multiples), and the deduction is a share of the tier's lower bound
        # dollar amount, rounded to the nearest dollar at each step. This
        # reproduces every published F-1 dollar amount except the size-11 180%
        # FPL bound, where DCF's own published schedule shows $10,917 while
        # the rule derives $10,914; we use the derived value.
        fpg_ratio = income / monthly_fpg
        tier_floor_bound = np.floor(p.tier_floor.calc(fpg_ratio) * monthly_fpg + 0.5)
        deduction = np.floor(p.rate.calc(fpg_ratio) * tier_floor_bound + 0.5)
        is_tanf = spm_unit("is_tanf_enrolled", period)
        return where(is_tanf, 0, deduction)

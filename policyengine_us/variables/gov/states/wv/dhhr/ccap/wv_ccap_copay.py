from policyengine_us.model_api import *


class wv_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "West Virginia CCAP family co-payment"
    definition_period = MONTH
    defined_for = StateCode.WV
    reference = (
        "https://bfa.wv.gov/media/6826/download?inline#page=1",
        "https://bfa.wv.gov/media/6766/download?inline#page=65",
        "https://bfa.wv.gov/media/39915/download?inline#page=39",
    )

    def formula(spm_unit, period, parameters):
        # Appendix A: daily co-payment per child looked up by family size and
        # FPL ratio. Manual §6.4.3.2: fees are daily, assessed for each child
        # in care. Manual §6.4.3.4: capped at three youngest children.
        p = parameters(period).gov.states.wv.dhhr.ccap.copayment
        countable_income = spm_unit("wv_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        fpl_ratio = where(fpg > 0, countable_income / fpg, 0)
        family_size = spm_unit("spm_unit_size", period.this_year)
        # Look up daily fee per child from Appendix A by family size column.
        # Families with twelve or more people use the eleven-person column.
        rate = p.rate
        daily_fee_per_child = select(
            [
                family_size == 1,
                family_size == 2,
                family_size == 3,
                family_size == 4,
                family_size == 5,
                family_size == 6,
                family_size == 7,
                family_size == 8,
                family_size == 9,
                family_size == 10,
            ],
            [
                rate.size_1.calc(fpl_ratio),
                rate.size_2.calc(fpl_ratio),
                rate.size_3.calc(fpl_ratio),
                rate.size_4.calc(fpl_ratio),
                rate.size_5.calc(fpl_ratio),
                rate.size_6.calc(fpl_ratio),
                rate.size_7.calc(fpl_ratio),
                rate.size_8.calc(fpl_ratio),
                rate.size_9.calc(fpl_ratio),
                rate.size_10.calc(fpl_ratio),
            ],
            default=rate.size_11.calc(fpl_ratio),
        )
        person = spm_unit.members
        is_eligible_child = person("wv_ccap_eligible_child", period)
        monthly_care_days = person(
            "childcare_attending_days_per_month", period.this_year
        )
        in_care = is_eligible_child & (monthly_care_days > 0)
        num_in_care = spm_unit.sum(in_care)
        total_monthly_days = spm_unit.sum(monthly_care_days * in_care)
        # Per Manual §6.4.3.4: fee waived for any child beyond the three
        # youngest. We don't track child ordering, so apply the cap as a
        # uniform 3/N scaling across all eligible children in care.
        billed_share = where(
            num_in_care > 0,
            min_(num_in_care, p.max_billed_children) / max_(num_in_care, 1),
            0,
        )
        uncapped_copay = daily_fee_per_child * total_monthly_days * billed_share
        # CCDF State Plan §3.1.1 caps the family fee at 7% of gross income.
        capped_copay = min_(uncapped_copay, countable_income * p.max_share)
        # Manual §6.4.1 / CCDF Plan §3.3.1: foster-care children pay no fee.
        # We don't track per-child fee waivers at the moment, so we waive the
        # whole family copay if any child is in foster care.
        # We don't track kinship-care placements (CCDF Plan §3.3.1(vi)),
        # CPS Safety/Treatment Plans (Manual §6.4.1), or protective-services
        # status (CCDF Plan §3.3.1(vi)) at the moment, so the corresponding
        # fee waivers are not applied.
        has_foster_child = add(spm_unit, period, ["is_in_foster_care"]) > 0
        return where(has_foster_child, 0, capped_copay)

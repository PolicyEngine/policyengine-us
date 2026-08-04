from policyengine_us.model_api import *


class ky_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Kentucky CCAP family copayment"
    definition_period = MONTH
    defined_for = StateCode.KY
    reference = (
        "https://apps.legislature.ky.gov/services/karmaservice/documents/10239/ToPDF?markup=false#page=11",
        "https://apps.legislature.ky.gov/law/kar/downloads/docs/15544/document.engrossed.pdf#page=12",
    )

    def formula(spm_unit, period, parameters):
        # 922 KAR 2:160 Section 11(3)(a): the "Family Co-Payment Per Day" table
        # sets a single per-family daily fee, looked up by monthly countable
        # income, family size (2/3/4/5+), and the number of children needing care
        # (one child vs two or more). The one-vs-two-or-more column already encodes
        # the child count, so the fee is the whole-family rate for a day of care --
        # not a per-child fee.
        # We don't track the 12-month copay freeze (Section 11(3)(c)) at the
        # moment, so the copay is recomputed each period from current income.
        # We don't track the discretionary Protection and Permanency copay waiver
        # (Section 5(3)) or court-ordered child-care payments substituting for the
        # copay (Section 11(2)) at the moment.
        p = parameters(period).gov.states.ky.dcbs.ccap.copay
        countable_income = spm_unit("ky_ccap_countable_income", period)
        family_size = spm_unit("spm_unit_size", period.this_year)

        person = spm_unit.members
        is_eligible_child = person("ky_ccap_eligible_child", period)
        monthly_care_days = person(
            "childcare_attending_days_per_month", period.this_year
        )
        in_care = is_eligible_child & (monthly_care_days > 0)
        num_in_care = spm_unit.sum(in_care)
        one_child = num_in_care <= 1

        # Section 11(3)(a): family size 2 has only a one-child column.
        scale_family_fee = select(
            [
                family_size <= 2,
                (family_size == 3) & one_child,
                family_size == 3,
                (family_size == 4) & one_child,
                family_size == 4,
                one_child,
            ],
            [
                p.size_2.calc(countable_income),
                p.size_3_one_child.calc(countable_income),
                p.size_3_two_or_more.calc(countable_income),
                p.size_4_one_child.calc(countable_income),
                p.size_4_two_or_more.calc(countable_income),
                p.size_5_plus_one_child.calc(countable_income),
            ],
            default=p.size_5_plus_two_or_more.calc(countable_income),
        )
        # Section 11(3)(b): the family's per-day copayment is capped at the maximum
        # daily copayment for a family with more than five members.
        daily_family_fee = min_(scale_family_fee, p.max_daily)
        # The fee is a per-family per-day charge, so it is assessed once per day of
        # care for the family -- not once per child-day. Families generally send
        # all children the same days; where children differ, the maximum care-day
        # count across children approximates the family's days with any child in
        # care without double-charging shared days.
        family_care_days = spm_unit.max(monthly_care_days * in_care)
        return daily_family_fee * family_care_days

    def formula_2024_11_18(spm_unit, period, parameters):
        # 922 KAR 2:160 (eff. 11-18-2024) Section 11(3)(a): the CCAP Daily
        # Co-Payment Chart sets a single per-family daily fee by gross monthly
        # income and household size. The chart lists the household-of-two fee;
        # each additional member reduces the fee by the per-member amount with
        # zero as the floor, and each full $300 of income above the chart's
        # highest band adds $1 to the household-size amount.
        # The chart's extension column reads "Deduct $1 for each additional
        # household member over age 6, with 0 being the lowest", but the column
        # itself prints the household-of-seven value as an unconditional $1
        # step below the household-of-six column, so we apply the deduction by
        # household size alone and don't track the ages of additional members.
        # We don't track the 12-month copay freeze (Section 11(3)(c)) or
        # court-ordered child-care payments substituting for the copay
        # (Section 11(2)) at the moment.
        p = parameters(period).gov.states.ky.dcbs.ccap.copay
        countable_income = spm_unit("ky_ccap_countable_income", period)
        family_size = spm_unit("spm_unit_size", period.this_year)
        base = p.base.calc(countable_income)
        escalation = (
            np.floor(max_(countable_income - p.escalation.start, 0) / p.escalation.band)
            * p.escalation.amount
        )
        reduction = (
            max_(family_size - p.base_household_size, 0) * p.household_size_reduction
        )
        # Section 11(3)(b): capped at the maximum daily copayment. The cap only
        # binds for households whose income stays eligible under the 85% SMI
        # limits, i.e. families with more than five members.
        daily_family_fee = min_(max_(base + escalation - reduction, 0), p.max_daily)
        # Section 5(3) (eff. 11-18-2024): the cabinet shall waive the family
        # copayment for a child participating in CCAP through a child
        # protective services authorization (Protection and Permanency).
        person = spm_unit.members
        is_protection_permanency = spm_unit.any(
            person("is_in_foster_care", period)
            | person("receives_or_needs_protective_services", period.this_year)
        )
        is_eligible_child = person("ky_ccap_eligible_child", period)
        monthly_care_days = person(
            "childcare_attending_days_per_month", period.this_year
        )
        in_care = is_eligible_child & (monthly_care_days > 0)
        # The fee is a per-family per-day charge, assessed once per day of care
        # for the family; the maximum care-day count across children
        # approximates the family's days with any child in care.
        family_care_days = spm_unit.max(monthly_care_days * in_care)
        return where(is_protection_permanency, 0, daily_family_fee * family_care_days)

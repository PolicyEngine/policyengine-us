from policyengine_us.model_api import *


class ky_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Kentucky CCAP family copayment"
    definition_period = MONTH
    defined_for = StateCode.KY
    reference = "https://apps.legislature.ky.gov/services/karmaservice/documents/10239/ToPDF?markup=false#page=11"

    def formula(spm_unit, period, parameters):
        # 922 KAR 2:160 Section 11(3): the family co-payment is a per-day fee per
        # child, looked up by monthly countable income, family size (2/3/4/5+),
        # and the number of children needing care (one child vs two or more).
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
        scale_fee_per_child = select(
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
        # Section 11(3)(b): the per-day fee per child is capped at the maximum
        # daily copayment for a family with more than five members.
        daily_fee_per_child = min_(scale_fee_per_child, p.max_daily)
        # The per-day fee is assessed for each child in care, for each day of care.
        total_monthly_days = spm_unit.sum(monthly_care_days * in_care)
        return daily_fee_per_child * total_monthly_days

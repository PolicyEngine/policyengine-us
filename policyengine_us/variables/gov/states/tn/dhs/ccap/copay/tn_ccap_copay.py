from policyengine_us.model_api import *


class tn_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Tennessee CCAP parent copay"
    definition_period = MONTH
    defined_for = StateCode.TN
    reference = (
        "https://www.tn.gov/content/dam/tn/human-services/documents/Income%20Eligibility%20Limits%20and%20CoPay%20Chart%2010.1.25.pdf#page=1",
        "https://www.tn.gov/content/dam/tn/human-services/documents/CCDF%20State%20Plan%20FFY%202025-2027%20Tennessee.pdf#page=46",
        "https://www.tn.gov/content/dam/tn/human-services/documents/CCDF%20State%20Plan%20FFY%202025-2027%20Tennessee.pdf#page=48",
        "https://www.tn.gov/content/dam/tn/human-services/documents/CCDF%20State%20Plan%20FFY%202025-2027%20Tennessee.pdf#page=49",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tn.dhs.ccap.copay
        countable_income = spm_unit("tn_ccap_countable_income", period)
        # The copay chart floors twice: the monthly dollar copay (5% of monthly
        # countable gross income) is floored to whole dollars, then divided by
        # 4.3 and floored again to the whole-dollar weekly copay. Chart example:
        # $1,895 x 0.05 = $94.75 -> $94 -> / 4.3 = $21.86 -> $21 per week.
        monthly_dollar_copay = np.floor(max_(countable_income, 0) * p.rate)
        weekly_copay = np.floor(monthly_dollar_copay / p.weeks_per_month)

        person = spm_unit.members
        is_eligible_child = person("tn_ccap_eligible_child", period)
        in_care = person("childcare_hours_per_week", period.this_year) > 0
        is_paying_child = is_eligible_child & in_care
        n_paying = spm_unit.sum(is_paying_child)

        # The weekly copay is split equally among children in care; part-time
        # children pay half of their share.
        is_part_time = person("tn_ccap_part_time", period)
        per_child_share = where(is_part_time, p.part_time_share, 1)
        total_share = spm_unit.sum(is_paying_child * per_child_share)
        per_child_weekly = np.divide(
            weekly_copay,
            n_paying,
            out=np.zeros_like(weekly_copay),
            where=n_paying > 0,
        )
        family_weekly_copay = per_child_weekly * total_share
        monthly_copay = family_weekly_copay * p.weeks_per_month

        # Before October 1, 2025 the copay is waived at or below 150% FPL.
        # From that date the threshold is 0, so only zero-income families
        # (who already owe nothing) are waived.
        fpg = spm_unit("spm_unit_fpg", period)
        fpl_ratio = where(fpg > 0, countable_income / fpg, 0)
        below_waiver = fpl_ratio <= p.fpl_waiver_threshold
        # Families First (TANF) recipients pay no copay.
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        # Protective-services children exempt the family from the copay.
        has_protective_child = (
            spm_unit.sum(
                is_eligible_child
                * person("receives_or_needs_protective_services", period.this_year)
            )
            > 0
        )
        # Families with a child enrolled in Head Start or Early Head Start are
        # exempt from the copay (State Plan Section 3.3.1.v, #page=49).
        has_head_start_child = (
            spm_unit.sum(
                is_eligible_child
                * person("is_enrolled_in_head_start", period.this_year)
            )
            > 0
        )
        waived = (
            below_waiver | tanf_enrolled | has_protective_child | has_head_start_child
        )
        return where(waived, 0, monthly_copay)

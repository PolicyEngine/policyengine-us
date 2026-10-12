from policyengine_us.model_api import *


class wi_shares_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Wisconsin Shares assistance group copayment"
    definition_period = MONTH
    defined_for = "wi_shares_eligible"
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=150",
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=154",
        "https://dcf.wisconsin.gov/files/wishares/pdf/wishares-copay-schedule.pdf",
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/III/155/5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wi.dcf.shares
        # The assistance group copayment is the copayment per hour times the
        # group's copayment hours, capped at 760 (five children at 152 hours;
        # Section 18.2).
        copay_hours = add(spm_unit, period, ["wi_shares_copay_hours"])
        capped_hours = min_(copay_hours, p.copay.hours.assistance_group_cap)
        copay_per_hour = spm_unit("wi_shares_copay_per_hour", period)
        base_copay = copay_per_hour * capped_hours
        # Exit period: enrolled assistance groups with income above 200% of
        # the federal poverty guideline pay an additional copayment of $1 for
        # every full $5 of income above the limit (Sections 18.2.1 and
        # 18.4.2; Wis. Stat. § 49.155(1m)(c)1d.a.). New applicants above the
        # limit are income-ineligible instead.
        enrolled = spm_unit("is_wi_shares_enrolled", period)
        countable_income = spm_unit("wi_shares_countable_income", period)
        monthly_fpg = spm_unit("spm_unit_fpg", period)
        initial_limit = monthly_fpg * p.income.limit.initial_fpg_rate
        excess_income = max_(countable_income - initial_limit, 0)
        # Compute and round the product in float64 so float32 noise at an
        # exact $5 multiple of excess income (e.g., 154.99998 instead of
        # 155) cannot drop a dollar from the floor; wi_shares_copay_per_hour
        # guards its band lookup the same way.
        exit_copay = where(
            enrolled,
            np.floor(
                np.round(
                    excess_income.astype(np.float64) * p.copay.exit.phase_out_rate,
                    5,
                )
            ),
            0,
        )
        # Assistance groups with a parent open for W-2 have a $0 copayment
        # type (Section 18.3); foster children are already excluded from the
        # copayment hours pool. Groups with no copayment hours owe no
        # copayment.
        is_tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        no_copay = is_tanf_enrolled | (capped_hours == 0)
        return where(no_copay, 0, base_copay + exit_copay)

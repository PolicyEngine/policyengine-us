from policyengine_us.model_api import *


class wi_shares_copay_per_hour(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Wisconsin Shares copayment per hour"
    definition_period = MONTH
    defined_for = "wi_shares_eligible"
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=150",
        "https://dcf.wisconsin.gov/files/wishares/pdf/wishares-copay-schedule.pdf",
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/III/155/5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wi.dcf.shares.copay.per_hour
        # The copayment schedule looks up the hourly copayment by the
        # assistance group's income as a share of the federal poverty
        # guideline (floored to the lower 5% line) and the number of children
        # with authorizations, capped at the five-or-more column
        # (Section 18.2). spm_unit_fpg is an annual dollar amount, so reading
        # it with the bare monthly period auto-divides it to a monthly value.
        countable_income = spm_unit("wi_shares_countable_income", period)
        monthly_fpg = spm_unit("spm_unit_fpg", period)
        # Compute and round the ratio in float64 so float32 noise at an
        # exact band edge (e.g., income at exactly 105% of the guideline
        # storing as 1.04999995) cannot drop the group into the lower band;
        # the exit-period copayment floor in wi_shares_copay uses the same
        # guard. The schedule prints whole-dollar income rows; looking up the
        # exact ratio instead can differ by one band within about $0.50 of a
        # row boundary (intentional).
        fpg_ratio = np.round(countable_income.astype(np.float64) / monthly_fpg, 5)
        # Only children subject to a regular copayment count toward the
        # column lookup; reduced-copay-type children (e.g., foster) are
        # excluded because Section 18.2 calculates their copayments
        # separately, and the handbook does not say which count a mixed
        # group uses. Income above 200% of the poverty guideline keeps the
        # top rate, with the exit-period copayment added in wi_shares_copay.
        person = spm_unit.members
        counted_children = spm_unit.sum(person("wi_shares_copay_hours", period) > 0)
        return select(
            [
                counted_children == 1,
                counted_children == 2,
                counted_children == 3,
                counted_children == 4,
                counted_children >= 5,
            ],
            [
                p.one_child.calc(fpg_ratio),
                p.two_children.calc(fpg_ratio),
                p.three_children.calc(fpg_ratio),
                p.four_children.calc(fpg_ratio),
                p.five_or_more_children.calc(fpg_ratio),
            ],
            default=0,
        )

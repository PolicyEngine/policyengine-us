from policyengine_us.model_api import *


class wa_pfml_weekly_benefit_amount(Variable):
    value_type = float
    entity = Person
    label = "Washington PFML weekly benefit amount"
    documentation = (
        "Weekly benefit amount under Washington Paid Family and Medical "
        "Leave. Applies the two-tier replacement formula in "
        "RCW 50A.15.020(5) and clips the result to the statutory minimum "
        "and maximum weekly benefit amounts. Despite the YEAR definition "
        "period, this variable represents a weekly dollar amount."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/rcw/default.aspx?cite=50A.15.020",
        "https://paidleave.wa.gov/app/uploads/2025/12/Paycheck-insert-2026-1.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wa.pfml
        aww = person("wa_pfml_average_weekly_wage", period)
        lower_threshold = p.lower_threshold_fraction * p.state_average_weekly_wage
        lower_benefit = p.lower_benefit_rate * min_(aww, lower_threshold)
        upper_benefit = p.upper_benefit_rate * max_(aww - lower_threshold, 0)
        raw_benefit = lower_benefit + upper_benefit
        # Per RCW 50A.15.020(6)(b): minimum is $100, or AWW if AWW < $100.
        # Using min_(min_amount, aww) as the floor naturally handles zero AWW
        # (no employment → floor=0 → benefit=0) and low AWW (floor=AWW).
        effective_min = min_(p.min_weekly_benefit_amount, aww)
        return clip(
            raw_benefit,
            effective_min,
            p.max_weekly_benefit_amount,
        )

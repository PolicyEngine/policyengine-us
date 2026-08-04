from policyengine_us.model_api import *


class ny_ui_weekly_payable(Variable):
    value_type = float
    entity = Person
    label = "New York unemployment insurance weekly payable amount"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/LAB/590"
    documentation = (
        "Hybrid partial-benefit rule. The paid amount follows the P803 "
        "hours-tier fraction times the weekly benefit rate; the earnings "
        "zero-gate (gross earnings at or above WBR + partial benefit credit) "
        "follows NY Lab. Law § 525 / § 590(5)(c). The two sources conflict for "
        "low-WBR, high-earnings weeks: e.g. WBR $150 / 12 hours / $260 earnings "
        "yields $0 here under the statutory gate versus $112.50 under pure P803. "
        "The statutory gate is deliberately retained."
    )
    defined_for = "ny_ui_monetarily_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.dol.unemployment_insurance.benefit
        weekly_benefit_rate = person("ny_ui_weekly_benefit_rate", period)
        partial_benefit_credit = person("ny_ui_partial_benefit_credit", period)
        gross_weekly_earnings = person("ny_ui_gross_weekly_earnings", period)
        weekly_hours_worked = person("ny_ui_weekly_hours_worked", period)
        hours_tier_rate = person("ny_ui_hours_tier_rate", period)
        earnings_cap_disqualified = gross_weekly_earnings > p.max_amount
        partially_employed = (weekly_hours_worked > 0) & ~earnings_cap_disqualified
        # Statutory § 525 / § 590(5)(c) earnings zero-gate: no partial payment
        # once gross earnings reach WBR + partial benefit credit. This gate is
        # retained even though the P803 hours-tier amount below would otherwise
        # pay a positive benefit for the same week (see class documentation).
        partial_payment_eligible = gross_weekly_earnings < (
            weekly_benefit_rate + partial_benefit_credit
        )
        # Paid amount follows the P803 hours-tier fraction of the WBR.
        partial_amount = hours_tier_rate * weekly_benefit_rate

        amount = select(
            [
                earnings_cap_disqualified,
                partially_employed & partial_payment_eligible,
                partially_employed & ~partial_payment_eligible,
            ],
            [
                0,
                partial_amount,
                0,
            ],
            default=weekly_benefit_rate,
        )
        return amount

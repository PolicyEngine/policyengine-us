from policyengine_us.model_api import *


class ny_ui_weekly_payable(Variable):
    value_type = float
    entity = Person
    label = "New York unemployment insurance weekly payable amount"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/LAB/590"
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
        partial_payment_eligible = gross_weekly_earnings < (
            weekly_benefit_rate + partial_benefit_credit
        )
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

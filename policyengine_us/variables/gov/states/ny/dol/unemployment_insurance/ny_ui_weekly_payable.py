from policyengine_us.model_api import *


class ny_ui_weekly_payable(Variable):
    value_type = float
    entity = Person
    label = "New York unemployment insurance weekly payable amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/LAB/590",
        "https://dol.ny.gov/system/files/documents/2025/10/p803-partial-ui-faqs-10-3-25.pdf#page=1",
    )
    documentation = (
        "Partial-unemployment benefit under the P803 hours-based system "
        "(Ch. 277 of the Laws of 2021 § 31, effective 2021-08-16), which "
        "replaced the earlier day/earnings-based reduction. The weekly amount "
        "is the hours-tier fraction of the weekly benefit rate. The only "
        "earnings test is the statutory ceiling: gross weekly earnings above "
        "the maximum benefit rate (e.g. $504 in 2025) disqualify the week "
        "entirely, regardless of hours. The NY Lab. Law § 525 / § 590(5)(c) "
        "earnings-taper regime is displaced by the hours-tier system and is "
        "not applied, consistent with ny_ui_hours_tier_rate."
    )
    defined_for = "ny_ui_monetarily_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.dol.unemployment_insurance.benefit
        weekly_benefit_rate = person("ny_ui_weekly_benefit_rate", period)
        gross_weekly_earnings = person("ny_ui_gross_weekly_earnings", period)
        hours_tier_rate = person("ny_ui_hours_tier_rate", period)
        # P803 earnings ceiling: gross earnings above the maximum benefit rate
        # disqualify the entire week, regardless of hours worked.
        earnings_cap_disqualified = gross_weekly_earnings > p.max_amount
        # Otherwise the paid amount is the hours-tier fraction of the WBR (the
        # 0-10 hour tier pays the full rate, so fully-unemployed weeks return
        # the WBR). No § 525 earnings taper is applied.
        return where(
            earnings_cap_disqualified,
            0,
            hours_tier_rate * weekly_benefit_rate,
        )

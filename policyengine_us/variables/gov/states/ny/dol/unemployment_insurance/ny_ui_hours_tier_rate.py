from policyengine_us.model_api import *


class ny_ui_hours_tier_rate(Variable):
    value_type = float
    entity = Person
    label = "New York unemployment insurance hours tier rate"
    definition_period = YEAR
    reference = (
        "https://dol.ny.gov/system/files/documents/2025/10/p803-partial-ui-faqs-10-3-25.pdf#page=1",
        "https://www.nysenate.gov/legislation/bills/2021/S7148",
    )
    documentation = (
        "Partial-unemployment benefit fraction from the hours-based tier system "
        "in NYSDOL P803, enacted by Ch. 277 of the Laws of 2021 § 31 (as added "
        "by Ch. 305 of the Laws of 2021 § 14). The NY Lab. Law § 590(5)(c) "
        "earnings-offset regime remains displaced by the § 31 hours-tier system, "
        "whose sunset awaits the IT certification required by Ch. 277 § 33."
    )
    defined_for = StateCode.NY

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.dol.unemployment_insurance
        weekly_hours_worked = person("ny_ui_weekly_hours_worked", period)
        return p.partial.hours_tiers.calc(weekly_hours_worked)

from policyengine_us.model_api import *


class ny_ui_hours_tier_rate(Variable):
    value_type = float
    entity = Person
    label = "New York unemployment insurance hours tier rate"
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/LAB/590"
    documentation = (
        "NY Lab. Law § 590(5)(c) defines partial-unemployment benefit reductions."
    )
    defined_for = StateCode.NY

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.dol.unemployment_insurance
        weekly_hours_worked = person("ny_ui_weekly_hours_worked", period)
        return p.partial.hours_tiers.calc(weekly_hours_worked)

from policyengine_us.model_api import *


class ia_cca_monthly_units(Variable):
    value_type = float
    entity = Person
    label = "Iowa CCA half-day units of care per month per child"
    definition_period = MONTH
    defined_for = "ia_cca_eligible_child"
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=3"

    def formula(person, period, parameters):
        # A unit of service is a half day of up to 5 hours of care
        # (IAC 441-170.1). PolicyEngine has no authorized-units input, so we
        # infer the monthly units of care from the child's scheduled child
        # care hours: weekly hours, annualized to a monthly figure, divided
        # by the hours in a unit. `childcare_hours_per_week` is YEAR-defined.
        hours_per_unit = parameters(period).gov.states.ia.hhs.cca.payment.hours_per_unit
        weekly_hours = person("childcare_hours_per_week", period.this_year)
        monthly_hours = weekly_hours * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        return monthly_hours / hours_per_unit

from policyengine_us.model_api import *


class MDCCSAgeGroup(Enum):
    REGULAR = "Regular"
    INFANT = "Infant"


class md_ccs_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = MDCCSAgeGroup
    default_value = MDCCSAgeGroup.REGULAR
    definition_period = MONTH
    defined_for = StateCode.MD
    label = "Maryland CCS child age group for rate purposes"
    reference = "https://earlychildhood.marylandpublicschools.org/families/child-care-scholarship-program/child-care-scholarship-rates"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.msde.ccs.payment
        age_months = person("age", period.this_year) * MONTHS_IN_YEAR
        return where(
            age_months < p.infant_age_threshold,
            MDCCSAgeGroup.INFANT,
            MDCCSAgeGroup.REGULAR,
        )

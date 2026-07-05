from policyengine_us.model_api import *


class basic_health_program_age_curve_amount_person(Variable):
    value_type = float
    entity = Person
    label = "Basic Health Program age-curve reference premium"
    unit = USD
    definition_period = MONTH
    defined_for = "basic_health_program_enrolled"
    reference = "https://www.cms.gov/cciio/programs-and-initiatives/health-insurance-market-reforms/state-rating"

    def formula(person, period, parameters):
        return (
            person.household("slcsp_age_0", period)
            * person("slcsp_age_curve_multiplier", period)
            * person.tax_unit("slcsp_age_curve_applies", period)
        )

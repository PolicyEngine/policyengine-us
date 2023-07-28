from policyengine_us.model_api import *


class in_eic_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Child-level eligiblity for parents filing Indiana EIC"
    documentation = "Whether a child whose parent filing for Indiana EIC meets the demographic requirements."
    defined_for = StateCode.IN

    def formula(person, period, parameters):
        p = parameters(period).gov.states["in"].tax.income.credits.eic.age
        is_19 = person("age", period) < p.age_child
        is_24 = person("age", period) < p.age_full_time_student
        full_time_student = person("is_full_time_student", period)
        child_disabled = person("is_disabled", period)
        return (is_19 | (is_24 & full_time_student)) | child_disabled

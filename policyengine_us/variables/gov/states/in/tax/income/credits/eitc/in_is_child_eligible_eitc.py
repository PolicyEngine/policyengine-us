from policyengine_us.model_api import *


class is_child_eligible_eitc(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Child-level eligiblity for parents filing Indiana EIC"
    documentation = "Whether a child whose parent filing for Indiana EIC meets the demographic requirements."
    defined_for = StateCode.ID

    def formula(person, period, parameters):
        is_19 = person("age", period) < 19
        is_24 = person("age", period) < 24
        full_time_student = person("is_full_time_student", period)
        child_disabled = person("is_disabled", period)
        return (is_19 | (is_24 & full_time_student)) | child_disabled

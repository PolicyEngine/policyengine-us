from policyengine_us.model_api import *


class al_tanf_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for the Alabama family assistance (TANF)"
    defined_for = StateCode.AL
    definition_period = YEAR
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/10/DHR-FAD-595-Oct.23.pdf"

    def formula(person, period, parameters):
        # First we check whether the person is a dependent
        dependend = person("is_tax_unit_dependent", period)
        # Second the check whether the dependent is under the age threshold
        age = person("age", period)
        p = parameters(period).gov.states.al.dhs.tanf
        eligible_dependent = age < p.age_limit.non_student
        # The age threshold is increased for studnets
        eligible_student = age < p.age_limit.student
        student = person("is_full_time_student", period)
        age_eligible = where(student, eligible_student, eligible_dependent)
        # Lastly we need to check the immigration status
        immigration_status = person("immigration_status", period)
        status = immigration_status.possible_values
        citizen = immigration_status == status.CITIZEN
        return dependend & age_eligible & citizen

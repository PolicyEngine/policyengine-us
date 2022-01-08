from openfisca_us.model_api import *


class is_person_demographic_tanf_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Person-level eligiblity for TANF based on age, pregnancy, etc."
    documentation = "Whether a person in a family applying for the Temporary Assistance for Needy Families program meets demographic requirements."

    def formula(person, period, parameters):
        child_0_17 = person("is_child", period)
        is_18 = person("age", period) == 18
        school_enrolled_18_year_old = person("is_in_school", period) & is_18
        pregnant = person("is_pregnant", period)
        return child_0_17 | school_enrolled_18_year_old | pregnant

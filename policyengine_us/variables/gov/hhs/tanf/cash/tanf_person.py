from policyengine_us.model_api import *


class tanf_person(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Per-capita TANF"
    documentation = (
        "Per-capita value of Temporary Assistance for Needy Families benefit."
    )
    unit = USD

    def formula(person, period, parameters):
        return person.spm_unit("tanf", period) / person.spm_unit.nb_persons()

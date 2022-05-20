from openfisca_us.model_api import *


class state_supplement(Variable):
    value_type = float
    entity = Person
    label = "SSI State Supplement"
    definition_period = YEAR
    documentation = (
        "SSI State Supplement for this person (split equally between couples)."
    )

    def formula(person, period, parameters):
        marital_unit = person.marital_unit
        ssi_eligible_people = marital_unit("ssi_eligible_people")
        marital_unit_ssp = marital_unit("marital_unit_state_supplement")
        return where(
            ssi_eligible_people > 0, marital_unit_ssp / ssi_eligible_people, 0
        )

from openfisca_us.model_api import *


class ssi(Variable):
    value_type = float
    entity = Person
    label = "Supplemental Security Income"
    unit = USD
    documentation = "SSI for this person (split equally between couples)."
    definition_period = YEAR

    def formula(person, period, parameters):
        marital_unit = person.marital_unit
        ssi_eligible_people = marital_unit("ssi_eligible_people", period)
        marital_unit_ssi = marital_unit("marital_unit_ssi", period)
        return where(
            ssi_eligible_people > 0, marital_unit_ssi / ssi_eligible_people, 0
        )

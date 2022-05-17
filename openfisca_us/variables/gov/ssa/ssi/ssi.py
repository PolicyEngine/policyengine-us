from openfisca_us.model_api import *


class ssi(Variable):
    value_type = float
    entity = Person
    label = "SSI"
    unit = USD
    documentation = "SSI for this person (split equally between couples)."
    definition_period = YEAR

    def formula(person, period, parameters):
        is_ssi_eligible = person("is_ssi_aged_blind_disabled", period)
        joint_application = person.marital_unit.sum(is_ssi_eligible) > 1
        marital_unit_ssi = person.marital_unit("marital_unit_ssi", period)
        return (
            is_ssi_eligible
            * marital_unit_ssi
            * where(joint_application, 1 / 2, 1)
        )

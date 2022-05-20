from openfisca_us.model_api import *


class marital_unit_ssi(Variable):
    value_type = float
    entity = MaritalUnit
    label = "SSI for a marital unit"
    unit = USD
    documentation = "SSI for this person (split equally between couples)."
    definition_period = YEAR

    def formula(person, period, parameters):
        eligible = person.marital_unit("ssi_eligible_people") > 0
        return eligible * max_(0, person.marital_unit("uncapped_ssi", period))

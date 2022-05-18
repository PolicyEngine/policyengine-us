from openfisca_us.model_api import *


class maximum_ssi(Variable):
    value_type = float
    entity = MaritalUnit
    label = "Maximum SSI"
    definition_period = YEAR

    def formula(marital_unit, period, parameters):
        person = marital_unit.members
        abd = person("is_ssi_aged_blind_disabled", period)
        joint = (marital_unit.sum(abd) > 1) | marital_unit(
            "ssi_deeming_occurs", period
        )
        ssi = parameters(period).ssa.ssi
        meets_resource_test = marital_unit("meets_ssi_resource_test", period)
        amount = MONTHS_IN_YEAR * where(
            joint, ssi.amount.couple, ssi.amount.individual
        )
        return marital_unit.any(abd) * amount * meets_resource_test

from openfisca_us.model_api import *


class taxsim_mstat(Variable):
    value_type = int
    entity = TaxUnit
    label = "Marital Status"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        marital_status = tax_unit("mars", period)
        marital = marital_status.possible_values
        return select(
            [
                marital_status == marital.SINGLE,
                marital_status == marital.HEAD_OF_HOUSEHOLD,
                marital_status == marital.JOINT,
                marital_status == marital.SEPARATE,
                marital_status == marital.WIDOW,
            ],
            [
                1,
                1,
                2,
                6,
                8,
            ],
        )

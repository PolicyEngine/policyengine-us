from openfisca_us.model_api import *


class in_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN exemptions"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return (
            in_base_exemptions
            + in_additional_exemptions
            + in_aged_blind_exemptions
            + in_aged_low_agi_exemptions
        )

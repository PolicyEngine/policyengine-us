from openfisca_us.model_api import *


class in_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN exemptions"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3"

    def formula(tax_unit, period, parameters):
        in_base_exemptions = tax_unit("in_base_exemptions", period)
        in_additional_exemptions = tax_unit("in_additional_exemptions", period)
        in_aged_blind_exemptions = tax_unit("in_aged_blind_exemptions", period)
        in_aged_low_agi_exemptions = tax_unit(
            "in_aged_low_agi_exemptions", period
        )
        return (
            in_base_exemptions
            + in_additional_exemptions
            + in_aged_blind_exemptions
            + in_aged_low_agi_exemptions
        )

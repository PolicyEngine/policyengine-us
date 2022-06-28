from gov.states.
from gov.states.
from gov.states.in.tax.income.exemptions.in_aged_blind_exemptions import in_aged_blind_exemptionsin.tax.income.exemptions.in_additional_exemptions import in_additional_exemptionsin.tax.income.exemptions.in_base_exemptions import in_base_exemptions
from openfisca_us.model_api import *


class in_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN exemptions"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        in_base_exemptions = tax_unit("in_base_exemptions", period)
        in_additional_exemptions = tax_unit("in_additional_exemptions", period)
        in_aged_blind_exemptions = tax_unit("in_aged_blind_exemptions", period)
        in_aged_low_agi_exemptions = tax_unit("in_aged_low_agi_exemptions", period)
        return (
            in_base_exemptions
            + in_additional_exemptions
            + in_aged_blind_exemptions
            + in_aged_low_agi_exemptions
        )

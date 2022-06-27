from openfisca_us.model_api import *


class in_additional_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN additional exemptions"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        additional_exemptions_count = tax_unit("in_additional_exemptions_count", period)
        p = parameters(
            period
        ).gov.states.in.tax.income.exemptions
        additional_exemption = p.additional_exemption.amount
        return additional_exemptions_count * additional_exemption
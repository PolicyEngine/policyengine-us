from openfisca_us.model_api import *


class md_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD income tax"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        refundable_credits = parameters(
            period
        ).gov.states.md.tax.income.refundable

        return add(refundable_credits)

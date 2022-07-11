from openfisca_us.model_api import *


class md_total_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Total Additions"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        additions = parameters(period).gov.states.md.tax.income.additions
        # Add lines 3, 4, and 5.
        return add(tax_unit, period, additions)

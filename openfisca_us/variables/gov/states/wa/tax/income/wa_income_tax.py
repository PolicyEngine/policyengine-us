from openfisca_us.model_api import *


class wa_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington income tax"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        in_wa = tax_unit.household("state_code_str", period) == "WA"
        wftc = tax_unit("wa_working_families_tax_credit", period)
        cap_gains = tax_unit("wa_capital_gains_tax", period)
        tax = cap_gains - wftc
        return tax * in_wa

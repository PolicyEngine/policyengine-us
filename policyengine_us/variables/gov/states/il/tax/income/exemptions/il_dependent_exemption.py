from policyengine_us.model_api import *


class il_dependent_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL dependent exemption"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        amount = parameters(
            period
        ).gov.states.il.tax.income.exemption.dependent

        return amount * tax_unit("tax_unit_dependents", period)

from policyengine_us.model_api import *
import numpy as np


class va_dependent_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "VA dependent exemption"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        amount = parameters(
            period
        ).gov.states.va.tax.income.deductions.itemized.child_dependent

        return np.where(
            tax_unit("tax_unit_dependents", period) < 2, amount, 2 * amount
        )

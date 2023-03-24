from policyengine_us.model_api import *
import numpy as np


class va_child_dependent_care_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "VA dependent exemption"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.deductions.itemized
        tax_unit_dependents = tax_unit("tax_unit_dependents", period)
        amount = p.child_dependent_deduction

        return np.where(
            tax_unit("tax_unit_dependents", period) > 2, 2*amount,  tax_unit("tax_unit_dependents", period)* amount
        )
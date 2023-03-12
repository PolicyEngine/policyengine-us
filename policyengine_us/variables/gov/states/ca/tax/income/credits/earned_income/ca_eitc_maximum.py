from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ca.tax.income.credits.earned_income.ca_eitc import (
    get_ca_eitc_branch,
)


class ca_eitc_maximum(Variable):
    value_type = float
    entity = TaxUnit
    label = "CalEITC maximum"
    unit = USD
    documentation = "California provides an earned income tax credit up to this value, based on the earned income amounts and phase-in rates, which vary with number of qualifying children."
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        branch = get_ca_eitc_branch(tax_unit, period, parameters)
        adjustment = parameters(
            period
        ).gov.states.ca.tax.income.credits.earned_income.adjustment.factor
        return branch.calculate("eitc_maximum", period) * adjustment

from policyengine_us.model_api import *

class ga_dependent_care_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia dependent care credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        expenses = spm_unit("childcare_expenses", period)
        rate = parameters(period).gov.states.ga.tax.income.main.qualified_child.rate
        return expenses * rate
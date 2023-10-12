from policyengine_us.model_api import *

class mt_child_dependent_care_expense_deduction_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana child dependent care expense deduction eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.deductions.standard.mt_child_dependent_care_expense_deduction.threshold
        agi = tax_unit("mt_agi", period)
        income_qualifies = agi <= p.threshold[qualifying_child]
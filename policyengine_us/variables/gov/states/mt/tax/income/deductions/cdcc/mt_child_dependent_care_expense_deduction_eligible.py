from policyengine_us.model_api import *

class mt_child_dependent_care_expense_deduction_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Montana child dependent care expense deduction"
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.deductions.standard.mt_child_dependent_care_expense_deduction
        agi = tax_unit("mt_agi", period)
        eligible_children = tax_unit("mt_child_dependent_care_expense_deduction_eligible_children", period)
        return agi <= p.threshold[eligible_children]

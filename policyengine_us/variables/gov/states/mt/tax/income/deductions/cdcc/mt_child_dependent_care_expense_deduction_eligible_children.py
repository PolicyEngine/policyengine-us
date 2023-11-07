from policyengine_us.model_api import *


class mt_child_dependent_care_expense_deduction_eligible_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "Montana child dependent care expense deduction"
    definition_period = YEAR
    defined_for = "mt_child_dependent_care_expense_deduction_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.standard.child_dependent_care_expense_deduction
        person = tax_unit.members
        age = person("age", period)
        dependent = person("is_tax_unit_dependent", period)

        qualifying_child = dependent & (
            (age <= p.threshold.age) | person("is_disabled", period)
        )

        return tax_unit.sum(qualifying_child)

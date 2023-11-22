from policyengine_us.model_api import *


class mt_child_dependent_care_expense_deduction_eligible_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "Montana child dependent care expense deduction eligible children"
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/2441-M_2022.pdf#page=1"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.child_dependent_care_expense
        person = tax_unit.members
        age = person("age", period)
        dependent = person("is_tax_unit_dependent", period)

        age_eligible = age < p.age_limit
        eligible = dependent & (age_eligible | person("is_disabled", period))  

        return tax_unit.sum(qualifying_child)

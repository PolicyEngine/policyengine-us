from policyengine_us.model_api import *

class mt_child_dependent_care_expense_deduction_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Determination of eligibility for Montana child dependent care expense deduction at the individual level"
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.child_dependent_care_expense
        age = person("age", period)
        dependent = person("is_tax_unit_dependent", period)
        age_eligible = age < p.age_limit
        return dependent & (age_eligible | person("is_disabled", period))

       
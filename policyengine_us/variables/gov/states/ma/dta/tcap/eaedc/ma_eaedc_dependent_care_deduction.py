from policyengine_us.model_api import *


class ma_eaedc_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Eligible for Massachusetts EAEDC dependent care deduction"
    unit = USD
    definition_period = YEAR
    defined_for = "ma_eaedc_dependent_care_deduction_eligible"
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-275#(B)"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.eaedc.deductions.dependent_care
        person = spm_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        meets_age_limit = age < p.age_threshold
        eligible_dependent = is_dependent & meets_age_limit
        # Calculate amount for each dependent
        dependent_care_expense_maximum = (
            p.maximum_expense.calc(age) * eligible_dependent
        )
        # add up the amount for each dependent
        total_capped_amount = spm_unit.sum(dependent_care_expense_maximum)
        dependent_care_expense = add(spm_unit, period, ["care_expenses"])
        return min_(dependent_care_expense, total_capped_amount)

from policyengine_us.model_api import *


class md_tca_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TCA childcare deduction"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.13.aspx"

    def formula(spm_unit, period, parameters):
        # Per COMAR 07.03.03.13.E(3)(c), childcare deduction is capped at
        # actual expenses, "not to exceed" per child based on employment
        # hours: $200/child for 100+ hours/month, $100/child for <100 hours.
        person = spm_unit.members
        is_child = person("is_child", period.this_year)
        num_children = spm_unit.sum(is_child)
        monthly_hours = person("monthly_hours_worked", period.this_year)
        max_monthly_hours = spm_unit.max(monthly_hours)
        p = parameters(period).gov.states.md.tca.income.deductions
        # Maximum deduction per child based on monthly work hours
        per_child_cap = p.childcare_expenses.cap.calc(max_monthly_hours)
        max_deduction = per_child_cap * num_children
        # Actual childcare expenses (capped at regulatory maximum).
        childcare_expenses = spm_unit("childcare_expenses", period)
        return min_(childcare_expenses, max_deduction)

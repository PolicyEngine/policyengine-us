from policyengine_us.model_api import *


class dc_tanf_childcare_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "DC Temporary Assistance for Needy Families (TANF) child care deduction per person"
    unit = USD
    definition_period = MONTH
    reference = "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.11"  # (A)(2)
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.dc.dhs.tanf.income.deductions.child_care
        child = person("is_child", period)
        dependent = person("is_tax_unit_dependent", period)
        eligible_child = child & dependent
        age = person("monthly_age", period)
        childcare_expenses = person("pre_subsidy_childcare_expenses", period)
        childcare_deduction = p.amount.calc(age) * eligible_child

        return min_(childcare_expenses, childcare_deduction)

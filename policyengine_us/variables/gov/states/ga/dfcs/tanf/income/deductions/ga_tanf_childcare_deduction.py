from policyengine_us.model_api import *


class ga_tanf_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia TANF childcare deduction"
    unit = USD
    definition_period = MONTH
    reference = ("https://pamms.dhs.ga.gov/dfcs/tanf/1615/",)
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.dfcs.tanf.income.deductions
        person = spm_unit.members
        dependent = person("is_tax_unit_dependent", period)
        age = person("monthly_age", period)
        childcare_expenses = spm_unit("childcare_expenses", period)

        # Georgia allows up to $200/month per child under 2,
        # and up to $175/month per child age 2 and older
        # Calculate max deduction per dependent based on age
        childcare_deduction_person = p.childcare.calc(age) * dependent
        total_childcare_deduction = spm_unit.sum(childcare_deduction_person)

        return min_(childcare_expenses, total_childcare_deduction)

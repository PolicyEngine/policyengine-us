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
        age = person("age", period.this_year)

        # Georgia allows up to $200/month per child under 2,
        # and up to $175/month per child age 2 and older
        max_deduction_per_child = p.childcare.calc(age)

        # Sum across all children in the SPM unit
        return spm_unit.sum(max_deduction_per_child)

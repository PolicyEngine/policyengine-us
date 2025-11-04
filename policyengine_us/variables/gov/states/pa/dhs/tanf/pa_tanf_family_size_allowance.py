from policyengine_us.model_api import *


class pa_tanf_family_size_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF Family Size Allowance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = (
        "55 Pa. Code Chapter 183, Appendix B, Table 3 - Family Size Allowances"
    )
    documentation = "The Family Size Allowance (FSA) for the budget group based on household size. This represents both the maximum monthly benefit amount and the income eligibility threshold (when compared to countable income). Pennsylvania has four benefit schedules based on county; this implementation uses Group 2 (Philadelphia County and most recipients). https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/chap183toc.html"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf.family_size_allowance

        # Use Group 2 schedule (Philadelphia County and most recipients)
        # This is a bracket schedule based on number of persons
        family_size = spm_unit.nb_persons()

        return p.group_2.calc(family_size)

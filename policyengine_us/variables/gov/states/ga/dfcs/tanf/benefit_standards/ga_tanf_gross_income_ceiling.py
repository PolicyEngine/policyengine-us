from policyengine_us.model_api import *


class ga_tanf_gross_income_ceiling(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia TANF gross income ceiling"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://pamms.dhs.ga.gov/dfcs/tanf/1525/",
        "https://pamms.dhs.ga.gov/dfcs/tanf/appendix-a/",
    )
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.dfcs.tanf.financial_standards

        # Gross income ceiling is 185% of the Standard of Need
        # per Ga. Comp. R. & Regs. 290-2-28-.02(j)
        standard_of_need = spm_unit("ga_tanf_standard_of_need", period)

        return standard_of_need * p.gross_income_ceiling_rate

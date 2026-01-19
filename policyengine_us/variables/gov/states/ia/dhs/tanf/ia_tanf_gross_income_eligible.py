from policyengine_us.model_api import *


class ia_tanf_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa TANF gross income eligible (Test 1)"
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27"

    def formula(spm_unit, period, parameters):
        gross_income = spm_unit("ia_tanf_gross_income", period)
        standard_of_need = spm_unit("ia_tanf_standard_of_need", period)
        p = parameters(period).gov.states.ia.dhs.tanf.income
        gross_income_limit = standard_of_need * p.gross_income_limit_percent
        return gross_income <= gross_income_limit

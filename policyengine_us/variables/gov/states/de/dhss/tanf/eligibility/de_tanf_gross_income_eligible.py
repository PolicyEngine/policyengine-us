from policyengine_us.model_api import *


class de_tanf_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Delaware TANF gross income eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008"
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        # Per DSSM 4008: Gross income <= 185% of Standard of Need
        standard_of_need = spm_unit("de_tanf_standard_of_need", period)
        p = parameters(period).gov.states.de.dhss.tanf.income
        gross_income_limit = standard_of_need * p.gross_limit

        gross_income = spm_unit("de_tanf_gross_income", period)

        return gross_income <= gross_income_limit

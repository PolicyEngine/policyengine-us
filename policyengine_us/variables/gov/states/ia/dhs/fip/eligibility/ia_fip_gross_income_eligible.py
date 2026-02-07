from policyengine_us.model_api import *


class ia_fip_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP gross income eligible"
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.41.pdf#page=20"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.dhs.fip.income
        gross_income = spm_unit("ia_fip_gross_income", period)
        standard_of_need = spm_unit("ia_fip_standard_of_need", period)
        gross_income_limit = standard_of_need * p.gross_income_limit_percent
        return gross_income <= gross_income_limit

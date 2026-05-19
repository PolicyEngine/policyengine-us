from policyengine_us.model_api import *


class nm_works_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Mexico Works gross income eligible"
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0520.html"
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        # Per 8.102.500.8(B) NMAC, gross income must be under 85% FPL
        p = parameters(period).gov.states.nm.hca.nm_works.income.gross_limit
        gross_income = spm_unit("nm_works_gross_income", period)
        fpg = spm_unit("tanf_fpg", period)
        return gross_income <= fpg * p.rate

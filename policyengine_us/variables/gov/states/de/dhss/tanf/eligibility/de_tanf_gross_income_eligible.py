from policyengine_us.model_api import *


class de_tanf_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Delaware TANF gross income eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/delaware/"
        "16-Del-Admin-Code-SS-4000-4008"
    )
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        # Per DSSM 4008: Gross income <= 185% of Standard of Need
        p = parameters(period).gov.states.de.dhss.tanf
        unit_size = spm_unit("spm_unit_size", period)
        capped_unit_size = min_(unit_size, p.payment_standard.max_unit_size)
        gross_income_limit = p.income.gross_limit.amount[capped_unit_size]

        gross_income = spm_unit("de_tanf_countable_gross_income", period)

        return gross_income <= gross_income_limit

from policyengine_us.model_api import *


class ky_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible for Kentucky Transitional Assistance Program due to income"
    )
    definition_period = MONTH
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
    defined_for = StateCode.KY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.tanf
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        gross_income = gross_earned + gross_unearned
        unit_size = spm_unit("spm_unit_size", period)
        capped_size = min_(unit_size, p.max_unit_size)
        gross_income_limit = p.gross_income_limit[capped_size]
        return gross_income <= gross_income_limit

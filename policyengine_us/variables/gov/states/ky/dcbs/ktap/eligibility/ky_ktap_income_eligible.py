from policyengine_us.model_api import *


class ky_ktap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Kentucky K-TAP due to income"
    definition_period = MONTH
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
    defined_for = StateCode.KY

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.dcbs.ktap.eligibility
        gross_income = add(
            spm_unit,
            period,
            ["tanf_gross_earned_income", "tanf_gross_unearned_income"],
        )
        standard_of_need = spm_unit("ky_ktap_standard_of_need", period)
        gross_income_limit = standard_of_need * p.gross_income_limit_rate
        return gross_income <= gross_income_limit

from policyengine_us.model_api import *


class ct_tfa_countable_income_at_application(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut Temporary Family Assistance (TFA) countable income at application"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CT
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/state-plans-and-federal-reports/tanf-state-plan/ct-tanf-state-plan-2024---2026---41524-amendment.pdf#page=10"

    adds = [
        "ct_tfa_countable_earned_income_at_application",
        "ct_tfa_countable_unearned_income",
    ]

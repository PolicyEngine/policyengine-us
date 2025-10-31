from policyengine_us.model_api import *


class ct_tfa_countable_income_at_application(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut Temporary Family Assistance (TFA) countable income at application"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CT
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf?rev=f9c7a2028b6e409689d213d1966d6818&hash=9DDB6100DBC3D983F7946E33D702B2C8#page=10"

    adds = [
        "ct_tfa_countable_earned_income_at_application",
        "ct_tfa_countable_unearned_income",
    ]

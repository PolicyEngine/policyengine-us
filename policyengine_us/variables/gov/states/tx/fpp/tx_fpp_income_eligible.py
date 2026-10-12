from policyengine_us.model_api import *


class tx_fpp_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Texas Family Planning Program income eligibility"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-382-109",
        "https://www.healthytexaswomen.org/healthcare-programs/family-planning-program/fpp-who-can-apply",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        income = spm_unit("tx_fpp_countable_income", period)
        income_limit = spm_unit("tx_fpp_income_limit", period)
        return income <= income_limit

from policyengine_us.model_api import *


class tx_fpp_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Texas Family Planning Program income eligibility"
    definition_period = YEAR
    reference = (
        "https://www.healthytexaswomen.org/healthcare-programs/family-planning-program/fpp-who-can-apply",
        "https://www.hhs.texas.gov/sites/default/files/documents/texas-womens-health-programs-report-2024.pdf",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        income = spm_unit("spm_unit_net_income", period)
        income_limit = spm_unit("tx_fpp_income_limit", period)
        return income <= income_limit

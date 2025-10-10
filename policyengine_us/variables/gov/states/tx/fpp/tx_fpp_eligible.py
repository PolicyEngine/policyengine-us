from policyengine_us.model_api import *


class tx_fpp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Texas Family Planning Program eligibility"
    definition_period = YEAR
    reference = (
        "https://www.healthytexaswomen.org/healthcare-programs/family-planning-program/fpp-who-can-apply",
        "https://www.hhs.texas.gov/sites/default/files/documents/texas-womens-health-programs-report-2024.pdf",
    )
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        age_eligible = person("tx_fpp_age_eligible", period)
        income_eligible = person.spm_unit("tx_fpp_income_eligible", period)
        return age_eligible & income_eligible

from policyengine_us.model_api import *


class tx_fpp_benefit(Variable):
    value_type = float
    entity = Person
    label = "Texas Family Planning Program benefit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.healthytexaswomen.org/healthcare-programs/family-planning-program/fpp-who-can-apply",
        "https://www.hhs.texas.gov/sites/default/files/documents/texas-womens-health-programs-report-2024.pdf",
    )
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        eligible = person("tx_fpp_eligible", period)
        p = parameters(period).gov.states.tx.fpp
        annual_benefit = p.annual_benefit
        return where(eligible, annual_benefit, 0)

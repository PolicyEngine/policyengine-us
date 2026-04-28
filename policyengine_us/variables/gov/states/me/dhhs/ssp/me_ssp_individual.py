from policyengine_us.model_api import *


class me_ssp_individual(Variable):
    value_type = float
    entity = Person
    label = "Maine SSP individual monthly amount"
    unit = USD
    definition_period = MONTH
    defined_for = "me_ssp_eligible"
    reference = (
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/144c332-2025-101%20%28AMD%29_0.docx",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/content/assets/144c332-appendices-charts.docx",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.me.dhhs.ssp.amount
        arrangement = person("me_ssp_living_arrangement", period)
        return p.individual[arrangement]

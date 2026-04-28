from policyengine_us.model_api import *


class me_ssp_couple(Variable):
    value_type = float
    entity = Person
    label = "Maine SSP per-person share of the couple monthly amount"
    unit = USD
    definition_period = MONTH
    defined_for = "me_ssp_eligible"
    reference = (
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/144c332-2025-101%20%28AMD%29_0.docx",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/content/assets/144c332-appendices-charts.docx",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.me.dhhs.ssp.amount
        category = person("me_ssp_payment_category", period)
        # Maine's couple amounts for D/E/F/G are not 2x the individual
        # amount -- they are the facility's couple rate covering both
        # spouses. Per-person attribution splits the couple total 50/50.
        return p.couple[category] / 2

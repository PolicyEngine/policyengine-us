from policyengine_us.model_api import *


class wi_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Wisconsin State SSI Supplement"
    definition_period = MONTH
    defined_for = StateCode.WI
    reference = (
        "https://docs.legis.wisconsin.gov/document/statutes/49.77",
        "https://www.emhandbooks.wisconsin.gov/ssi-admin/2/2.1_federal_and_state_ssi_recipients.htm",
    )

    def formula(person, period, parameters):
        # This models federal-linked recipients. Grandfathered state-only
        # recipients can qualify without federal SSI; their protected award
        # and unresolved new SSI-E certification budget are documented in
        # wi_ssi_e rather than inferred from the ordinary payment schedule.
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        institutional = person("ssi_lives_in_medical_treatment_facility", period)
        continuation = person("wi_ssp_institutional_continuation", period)
        incarcerated = person("is_incarcerated", period)
        return receives_ssi & ~incarcerated & (~institutional | continuation)

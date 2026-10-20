from policyengine_us.model_api import *


class va_eap_disabled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Disabled under Virginia EAP"
    documentation = "Person with a disability, a Social Security disability benefit, or SSI received on the basis of disability. Railroad Retirement disability, 100% Veterans Administration disability and Medicaid certification of permanent and total disability are covered only through is_disabled."
    reference = (
        # PDF pages 31, 52
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/eap/Complete_Manual.pdf#page=31",
        "https://law.lis.virginia.gov/admincodefull/title22/agency40/chapter680/",
    )
    defined_for = StateCode.VA

    def formula(person, period, parameters):
        # Manual B.6.c: "A disabled individual is a person who is receiving
        # Social Security disability, Railroad Retirement disability,
        # Supplemental Security Income as disabled, 100% Veterans
        # Administration disability benefits, or who has been certified as
        # permanently and totally disabled for Medicaid purposes."
        social_security_disability = person("social_security_disability", period) > 0
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        ssi_disabled = receives_ssi & person("is_ssi_disabled", period)
        return person("is_disabled", period) | social_security_disability | ssi_disabled

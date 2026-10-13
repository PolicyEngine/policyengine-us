from policyengine_us.model_api import *


class wi_ssp_countable_for_hud(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin SSI supplement countable for HUD"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.WI
    reference = (
        "https://www.law.cornell.edu/cfr/text/24/5.609",
        "https://www.dhs.wisconsin.gov/publications/p20679-26-01.pdf#page=24",
        "https://www.hud.gov/sites/dfiles/OCHCO/documents/2023-27pihn.pdf#page=81",
        # PDF pages 3-4
        "https://www.hud.gov/sites/dfiles/OCHCO/documents/2024-38pihn.pdf#page=3",
    )

    def formula(person, period, parameters):
        # Source conflict: SSI-E Handbook 4.1.1 counts SSI-E; 24 CFR 5.609(b)(19)
        # governs.
        # HUD person with disabilities (42 U.S.C. 1437a(b)(3)(E)), as in
        # is_hud_elderly_disabled_family, plus blindness.
        disabled = (
            person("is_disabled", period.this_year)
            | person("is_ssi_disabled", period.this_year)
            | (person("social_security_disability", period) > 0)
            | person("is_blind", period.this_year)
        )
        excluded = (
            disabled
            & person("wi_ssi_e_for_home_care", period)
            & ~person("ssi_lives_in_medical_treatment_facility", period)
        )
        return person("wi_ssp", period) - excluded * person("wi_ssi_e", period)

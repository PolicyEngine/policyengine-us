from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    household_member_indices,
)


class wi_ssp_countable_for_hud(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin SSI supplement countable for HUD"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.WI
    reference = (
        "https://www.law.cornell.edu/cfr/text/24/5.609",
        "https://www.hud.gov/sites/dfiles/OCHCO/documents/2023-27pihn.pdf#page=81",
        "https://www.hud.gov/sites/dfiles/OCHCO/documents/2024-38pihn.pdf#page=3",
    )

    def formula(person, period, parameters):
        caregiver_id = person("wi_ssi_e_caregiver_id", period.this_year)
        person_id = person("person_id", period.this_year)
        own_row = np.arange(person.count)
        hud_family = person.spm_unit.reference_entity.members_entity_id
        matches = np.zeros(person.count, dtype=int)
        family_caregiver = np.zeros(person.count, dtype=bool)
        for member in household_member_indices(person):
            named = (
                (member >= 0)
                & (caregiver_id != 0)
                & (caregiver_id == person_id[member])
            )
            matches = matches + named
            family_caregiver = family_caregiver | (
                named & (member != own_row) & (hud_family[member] == hud_family)
            )
        disabled = person("is_disabled", period.this_year) | person(
            "is_blind", period.this_year
        )
        qualifies = (
            disabled
            & person("wi_ssi_e_for_home_care", period)
            & ~person("ssi_lives_in_medical_treatment_facility", period)
            & (matches == 1)
            & family_caregiver
        )
        return person("wi_ssp", period) - qualifies * person("wi_ssi_e", period)

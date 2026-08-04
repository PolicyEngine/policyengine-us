from policyengine_us.model_api import *


class ca_sf_caap_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Counts toward the San Francisco County CAAP budget unit"
    definition_period = MONTH
    defined_for = "in_san_francisco"
    reference = (
        # SF Administrative Code SEC. 20.7-6 / 20.7-14 (aid from other
        # programs bars CAAP).
        "https://codelibrary.amlegal.com/codes/san_francisco/latest/sf_admin/0-0-0-65352",
        # CAAP Eligibility Manual, "One Spouse Receiving SSI Or CAPI, Only One
        # Spouse Applying For/On Aid": the bar keys on RECEIVING SSI or CAPI,
        # and the remaining applicant draws the one-person grant against their
        # own income.
        "https://www.sfhsa.org/sites/default/files/media/document/2026-06/manual_caap_eligibility_6_9_2026_v2.pdf#page=152",
    )

    def formula(person, period, parameters):
        # A person counts toward the CAAP budget unit only if they are not served
        # by an individual SSI-type cash program and have a qualified immigration
        # status (SEC. 20.7-6, 20.7-14). SSI recipients are served by SSI/SSP, and
        # aged/blind/disabled immigrants receiving CAPI are served by CAPI; both
        # are individual programs, so the bar applies per person (SSIP, a CAAP
        # sub-program, serves SSI-pending applicants). Both bars key on receipt,
        # not categorical eligibility: a categorically CAPI-eligible person whose
        # income or resources leave them with no CAPI payment is not served by
        # CAPI and stays in the CAAP budget unit (with their income counted).
        # ca_capi is computed at the SPM-unit level, so unit receipt is projected
        # down and intersected with the person-level categorical flag, which is
        # what ca_capi's own payment standard and countable income are masked by.
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        receives_capi = person("ca_capi_eligible_person", period.this_year) & (
            person.spm_unit("ca_capi", period.this_year) > 0
        )
        immigration_status_eligible = person(
            "ca_sf_caap_immigration_status_eligible", period
        )
        return ~receives_ssi & ~receives_capi & immigration_status_eligible

from policyengine_us.model_api import *


class ca_sf_caap_other_aid_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for San Francisco County CAAP due to other-aid bar"
    definition_period = MONTH
    defined_for = "in_san_francisco"
    reference = (
        # SF Administrative Code Chapter 20, Article VII (County Adult
        # Assistance Programs), SEC. 20.7-6.
        "https://codelibrary.amlegal.com/codes/san_francisco/latest/sf_admin/0-0-0-65352",
        # CAAP Eligibility Manual, 91-2 Eligibility to Other Assistance
        # Programs.
        "https://www.sfhsa.org/sites/default/files/media/document/2026-05/manual_caap_eligibility_5_14_2026.pdf#page=34",
    )

    def formula(spm_unit, period, parameters):
        # The CAAP Manual bars applicants who are recipients of other cash-aid
        # programs (SSI/SSP, CalWORKs, CAPI). SSI receipt is handled per-person
        # in ca_sf_caap_ineligible_person. Here we bar CalWORKs and CAPI, the
        # two remaining programs with a PolicyEngine variable. The manual also
        # lists RCA (Refugee Cash Assistance) and ECA (Entrant Cash Assistance),
        # but we don't have a PolicyEngine variable for either at the moment, so
        # they are not modeled. We model "recipient of" (benefit > 0), not the
        # broader "eligible to but not receiving" bar.
        receives_calworks = spm_unit("ca_tanf", period.this_year) > 0
        receives_capi = spm_unit("ca_capi", period.this_year) > 0
        return ~receives_calworks & ~receives_capi

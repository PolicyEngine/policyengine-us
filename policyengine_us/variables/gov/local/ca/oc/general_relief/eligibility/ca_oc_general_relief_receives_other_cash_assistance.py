from policyengine_us.model_api import *


class ca_oc_general_relief_receives_other_cash_assistance(Variable):
    value_type = bool
    entity = Person
    label = "Receives other cash assistance that excludes Orange County General Relief"
    definition_period = MONTH
    defined_for = "in_oc"
    reference = "https://www.ssa.ocgov.com/sites/ssa/files/2026-01/GR%20Reg%20SECTION%2020%20-%20Approved%20-%20January%202026.pdf#page=3"

    def formula(person, period, parameters):
        # Section 20.4.b excludes recipients of "another type of public
        # assistance (SSI/SSP, CalWORKs, Refugee Cash Assistance (RCA))"; the
        # list is non-exhaustive ("include but are not limited to"), so CAPI --
        # California's SSI-equivalent cash aid for immigrants -- is also an
        # excluding program. CAPI recipients do NOT have ssi > 0, so ca_capi is
        # checked separately.
        # CalWORKs and CAPI receipt are only available at the SPM-unit level, so
        # any unit receiving them excludes its members; this does not
        # distinguish child-only cases. Refugee Cash Assistance has no
        # California variable in PolicyEngine, so we don't track RCA at the
        # moment.
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        # Read the take-up-gated federal aggregator rather than ca_tanf
        # directly (matching the ssi arm) so declined take-up lifts the
        # exclusion; for a California household, tanf equals CalWORKs.
        receives_calworks = (person.spm_unit("tanf", period) > 0) | person.spm_unit(
            "receives_tanf", period
        )
        receives_capi = person.spm_unit("ca_capi", period) > 0
        return receives_ssi | receives_calworks | receives_capi

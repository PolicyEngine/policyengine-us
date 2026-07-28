from policyengine_us.model_api import *


class ca_sbd_general_relief_receives_other_cash_assistance(Variable):
    value_type = bool
    entity = Person
    label = "Receives other cash assistance that excludes San Bernardino County General Relief"
    definition_period = MONTH
    defined_for = "in_sbd"
    reference = (
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/9e5e1b1a-e577-4f84-92c4-86574a9ff0cf.docx",
        "https://wp.sbcounty.gov/tad/wp-content/uploads/sites/25/2025/06/gr000101-4.pdf#page=2",
    )

    def formula(person, period, parameters):
        # GR will not be utilized to subsidize any other cash assistance
        # program; the handbook names SSI/SSP and CalWORKs recipients as
        # supported by other public funds. CAPI is deliberately not barred
        # here, since the handbook names only SSI/SSP and CalWORKs.
        # SSI is person-level, so only the individual recipient is barred.
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        # SSP is computed at the SPM-unit level, so unit receipt is projected
        # down and intersected with the person-level categorical flag
        # (mirroring the SF CAAP CAPI bar): only the aged, blind, or disabled
        # member an SSP-only payment serves is barred, not the whole unit.
        receives_ssp = person("ca_state_supplement_eligible_person", period) & (
            person.spm_unit("ca_state_supplement", period) > 0
        )
        # CalWORKs receipt is tracked at the SPM-unit level, so a unit
        # receiving it bars its members. Read the take-up-gated federal
        # aggregator rather than ca_tanf directly (matching the ssi arm) so
        # declined take-up lifts the bar; for a California household, tanf
        # equals CalWORKs.
        receives_calworks = (person.spm_unit("tanf", period) > 0) | person.spm_unit(
            "receives_tanf", period
        )
        return receives_ssi | receives_ssp | receives_calworks

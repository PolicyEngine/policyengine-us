from policyengine_us.model_api import *


class md_meap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Maryland MEAP qualified household size"
    defined_for = StateCode.MD
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/07.03.21.04",
        # PDF pages 107, 108.
        "https://dhs.maryland.gov/documents/OHEP/OHEP-Operations-Manual.pdf#page=107",
    )
    documentation = (
        "Follows COMAR 07.03.21.04C: nonqualified members are excluded from size and "
        "their income counts in full. The May 2025 manual instead includes all "
        "children under 18 regardless of status; this unresolved conflict is recorded "
        "explicitly, and this draft follows the regulation. SPM membership "
        "approximates the energy-sharing household. No SNAP-specific immigration bars "
        "apply."
    )

    adds = ["is_citizen_or_legal_immigrant"]

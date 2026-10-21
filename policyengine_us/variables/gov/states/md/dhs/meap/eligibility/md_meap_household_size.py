from policyengine_us.model_api import *


class md_meap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Maryland MEAP qualified household size"
    defined_for = StateCode.MD
    reference = (
        # PDF pages 107, 108.
        "https://dhs.maryland.gov/documents/OHEP/OHEP-Operations-Manual.pdf#page=108",
        "https://regs.maryland.gov/us/md/exec/comar/07.03.21.04",
    )
    documentation = (
        "Follows the May 2025 manual (page 108): every child under 18 counts "
        "regardless of immigration status, nonqualified adults are excluded from "
        "size, and every member's income counts in full. COMAR 07.03.21.04C(1) would "
        "exclude every nonqualified member; the manual is the operating rule. SPM "
        "membership approximates the energy-sharing household. No SNAP-specific "
        "immigration bars apply."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.dhs.meap
        person = spm_unit.members
        # Manual page 108: "Children under 18 are always counted in the
        # household, regardless of citizenship status"; ineligible adults are
        # not counted.
        child = person("age", period) < p.adult_age
        qualified = person("is_citizen_or_legal_immigrant", period)
        return spm_unit.sum(qualified | child)

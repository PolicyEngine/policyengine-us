from policyengine_us.model_api import *


class ny_heap_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP categorical income eligibility"
    defined_for = StateCode.NY
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-393.4",
        "https://liheapch.acf.gov/docs/2026/state-plans/NY_Plan_2026.pdf#page=5",
        # PDF pages 37, 110.
        "https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=37",
    )
    documentation = (
        "Receipt of SNAP, TANF or Code A SSI. 18 NYCRR 393.4(c)(1)(iii) and the "
        "manual glossary define Code A as an SSI individual or couple living alone "
        "in the federal own-household arrangement, so the SPM unit may hold no one "
        "but the recipient or the recipient couple, foster members aside. Recurring "
        "receipt on the application date is approximated; expedited/emergency-only "
        "benefits and roomer-only awards cannot be distinguished. Chapter 8 D.10 "
        "also qualifies Safety Net Assistance, but no NY-specific receipt input "
        "identifies it."
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        arrangement = person("ssi_federal_living_arrangement", period.first_month)
        own_household = arrangement == arrangement.possible_values.OWN_HOUSEHOLD
        receives_ssi = (person("ssi", period) > 0) | (
            add(person, period, ["receives_ssi"]) > 0
        )
        foster = person("is_in_foster_care", period.first_month)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # State Code A is "living alone": one eligible individual or one
        # eligible couple (14-ADM-07), so every non-foster member must be an
        # SSI recipient who is the head or spouse.
        living_alone = spm_unit.all(foster | (receives_ssi & head_or_spouse))
        qualifying_ssi = living_alone & spm_unit.any(
            receives_ssi
            & own_household
            & person("is_citizen_or_legal_immigrant", period)
            & ~person("ny_heap_is_excluded_person", period)
        )
        return (add(spm_unit, period, ["snap", "tanf"]) > 0) | qualifying_ssi

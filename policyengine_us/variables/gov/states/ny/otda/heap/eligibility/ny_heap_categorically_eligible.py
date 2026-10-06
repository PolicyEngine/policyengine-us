from policyengine_us.model_api import *


class ny_heap_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP categorical income eligibility"
    defined_for = StateCode.NY
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/NY_Plan_2026.pdf#page=5",
        # PDF pages 37, 110.
        "https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=37",
    )
    documentation = (
        "Receipt of SNAP, TANF or SSI in a federal own-household arrangement. State "
        "SSI Code A and recurring receipt on the application date are approximated; "
        "expedited/emergency-only benefits and roomer-only awards cannot be "
        "distinguished. Chapter 8 D.10 also qualifies Safety Net Assistance, but no "
        "NY-specific receipt input identifies it."
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        arrangement = person("ssi_federal_living_arrangement", period.first_month)
        code_a = arrangement == arrangement.possible_values.OWN_HOUSEHOLD
        qualifying_ssi = spm_unit.any(
            (person("ssi", period) > 0)
            & code_a
            & person("is_citizen_or_legal_immigrant", period)
            & ~person("ny_heap_is_excluded_person", period)
        )
        return (add(spm_unit, period, ["snap", "tanf"]) > 0) | qualifying_ssi

from policyengine_us.model_api import *


class ny_heap_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New York HEAP categorical income eligibility"
    defined_for = StateCode.NY
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/NY_Plan_2026.pdf#page=5",
        "https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=37,110",
    )
    documentation = "Receipt of SNAP, federally funded NY TANF or SSI in a federal own-household arrangement. State SSI Code A and recurring receipt on the application date are approximated; expedited/emergency-only benefits and roomer-only awards cannot be distinguished. Safety Net Assistance is not treated as federally funded TANF."

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        arrangement = person("ssi_federal_living_arrangement", period.first_month)
        code_a = arrangement == arrangement.possible_values.OWN_HOUSEHOLD
        qualifying_ssi = spm_unit.any((person("ssi", period) > 0) & code_a)
        return (add(spm_unit, period, ["snap", "ny_tanf"]) > 0) | qualifying_ssi

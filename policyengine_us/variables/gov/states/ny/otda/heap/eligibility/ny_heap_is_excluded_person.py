from policyengine_us.model_api import *


class ny_heap_is_excluded_person(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Person excluded from the New York HEAP household"
    defined_for = StateCode.NY
    # Chapter 8 D.4(a)(3), (5), PDF page 36. This is the federal Code C,
    # distinct from the state Code A required for categorical SSI eligibility.
    reference = "https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=36"

    def formula(person, period, parameters):
        # January living arrangements approximate the application-month status.
        foster = person("is_in_foster_care", period.first_month)
        arrangement = person("ssi_federal_living_arrangement", period.first_month)
        code_c = arrangement == arrangement.possible_values.CHILD_IN_PARENTAL_HOUSEHOLD
        receives_ssi = (person("ssi", period) > 0) | (
            add(person, period, ["receives_ssi"]) > 0
        )
        return foster | (code_c & receives_ssi)

from policyengine_us.model_api import *


class sd_cca_expected_to_graduate(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Expected to graduate from school for South Dakota CCA"
    defined_for = StateCode.SD
    documentation = (
        "Whether the school-enrolled child is expected to graduate, as required "
        "for the under-19 extension by ARSD 67:47:01:03(3)-(4). School enrollment "
        "is tested separately; the rule does not require full-time enrollment or "
        "graduation before age 19."
    )
    reference = "https://sdlegislature.gov/Rules/Administrative/67:47:01:03"

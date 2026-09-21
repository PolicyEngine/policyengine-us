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
        "graduation before age 19. Defaults to school enrollment and can be "
        "overridden per person."
    )
    reference = (
        "https://sdlegislature.gov/Rules/Administrative/67:47:01:03",
        "https://dss.sd.gov/docs/childcare/assistance/BEES_CCA_Policy_Manual.pdf#page=18",
    )

    def formula(person, period, parameters):
        # NOTE: default only. ARSD 67:47:01:03(3)-(4) ties the graduation
        # expectation to school enrollment, so an enrolled child is assumed to
        # be expected to graduate unless this input is set explicitly.
        return person("is_in_k12_school", period)

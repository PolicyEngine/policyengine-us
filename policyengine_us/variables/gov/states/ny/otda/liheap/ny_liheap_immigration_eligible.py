from policyengine_us.model_api import *


class ny_liheap_immigration_eligible(Variable):
    value_type = bool
    entity = Person
    label = "NY HEAP immigration status eligible"
    definition_period = YEAR
    defined_for = StateCode.NY
    documentation = """Determines if a person meets immigration status requirements for NY HEAP.
    At least one household member must be a U.S. citizen or qualified immigrant."""

    def formula(person, period, parameters):
        # HEAP requires at least one household member to be:
        # - U.S. citizen, or
        # - Qualified immigrant (LPR, refugee, asylee, etc.)

        is_citizen = person("is_citizen", period)
        # Using is_qualified_immigrant which includes LPRs, refugees, asylees, etc.
        is_qualified = person("is_qualified_immigrant", period)

        return is_citizen | is_qualified

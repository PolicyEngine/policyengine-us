from policyengine_us.model_api import *


class has_marketplace_health_coverage(Variable):
    value_type = bool
    entity = Person
    label = "Deprecated legacy modeled Marketplace health coverage input"
    definition_period = YEAR
    default_value = True
    documentation = """
    Deprecated legacy modeled Marketplace coverage status.

    Use has_marketplace_health_coverage_at_interview for reported Marketplace
    coverage from survey data, and takes_up_aca_if_eligible for modeled ACA
    Marketplace take-up. ACA PTC eligibility does not depend on this variable.
    """

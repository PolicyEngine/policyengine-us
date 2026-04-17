from policyengine_us.model_api import *


class has_marketplace_health_coverage(Variable):
    value_type = bool
    entity = Person
    label = "Person has modeled Marketplace health coverage"
    definition_period = YEAR
    default_value = True
    documentation = """
    Legacy modeled Marketplace coverage status.

    Use has_marketplace_health_coverage_at_interview for reported current
    Marketplace coverage from survey data.
    """

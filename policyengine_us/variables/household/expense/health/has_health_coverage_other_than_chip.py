from policyengine_us.model_api import *


class has_health_coverage_other_than_chip(Variable):
    value_type = bool
    entity = Person
    label = "Person currently has health coverage other than CHIP"
    definition_period = YEAR
    documentation = """
    Partner-provided aggregate input for current health coverage sources that
    should disqualify a person from CHIP eligibility. This should exclude CHIP
    itself and Indian Health Service-only coverage.
    """

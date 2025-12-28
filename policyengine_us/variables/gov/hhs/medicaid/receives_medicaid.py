from policyengine_us.model_api import *


class receives_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Currently receives Medicaid"
    definition_period = YEAR
    documentation = """
    Input variable indicating a person currently has Medicaid coverage.
    Used to model continuous coverage for existing enrollees who may no
    longer meet eligibility criteria under new rules (e.g., CA undocumented
    immigrant enrollment freeze starting 2026).

    This differs from medicaid_enrolled which is computed based on
    eligibility and takeup rate.
    """

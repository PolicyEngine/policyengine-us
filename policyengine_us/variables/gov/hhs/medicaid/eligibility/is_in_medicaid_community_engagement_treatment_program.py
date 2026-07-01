from policyengine_us.model_api import *


class is_in_medicaid_community_engagement_treatment_program(Variable):
    value_type = bool
    entity = Person
    label = (
        "Participates in qualifying treatment program for Medicaid community engagement"
    )
    definition_period = YEAR
    default_value = False
    documentation = (
        "Whether the person participates in a qualifying drug addiction or "
        "alcoholic treatment and rehabilitation program for the Medicaid "
        "community engagement exclusion. State-specific minimum time "
        "commitments are not modeled."
    )
    reference = "https://www.govinfo.gov/content/pkg/FR-2026-06-03/pdf/2026-11094.pdf"

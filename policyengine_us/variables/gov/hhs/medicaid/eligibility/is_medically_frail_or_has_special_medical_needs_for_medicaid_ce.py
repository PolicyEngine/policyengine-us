from policyengine_us.model_api import *


class is_medically_frail_or_has_special_medical_needs_for_medicaid_ce(Variable):
    value_type = bool
    entity = Person
    label = (
        "Medically frail or has special medical needs for Medicaid community engagement"
    )
    documentation = (
        "Whether this person qualifies for the Medicaid community engagement "
        "medically frail or special medical needs exclusion. The full CMS "
        "definition depends on state condition lists and case review, so this "
        "input lets household situations represent people not captured by "
        "narrower disability variables."
    )
    definition_period = YEAR
    default_value = False
    reference = (
        "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=242",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/cib12082025.pdf",
        "https://www.govinfo.gov/content/pkg/FR-2026-06-03/pdf/2026-11094.pdf#page=125",
        "https://www.govinfo.gov/content/pkg/FR-2026-06-03/pdf/2026-11094.pdf#page=59",
    )

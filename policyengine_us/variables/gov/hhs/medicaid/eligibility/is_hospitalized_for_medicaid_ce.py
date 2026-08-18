from policyengine_us.model_api import *


class is_hospitalized_for_medicaid_ce(Variable):
    value_type = bool
    entity = Person
    label = (
        "Hospitalized or receiving intensive services for Medicaid community engagement"
    )
    documentation = (
        "Whether the person qualifies for the Medicaid community engagement "
        "short-term hardship exception because they are hospitalized or "
        "receiving intensive outpatient or inpatient services. The exception "
        "is applied when the circumstance is present; this input lets "
        "household situations represent it since survey data lack a hospital "
        "utilization signal. It defaults to false, so it does not affect "
        "microsimulation results."
    )
    definition_period = YEAR
    default_value = False
    reference = (
        "https://www.govinfo.gov/content/pkg/FR-2026-06-03/pdf/2026-11094.pdf",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/cib12082025.pdf#page=6",
    )

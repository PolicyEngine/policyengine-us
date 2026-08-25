from policyengine_us.model_api import *


class is_hospitalized_for_medicaid_ce(Variable):
    value_type = bool
    entity = Person
    label = (
        "Hospitalized or receiving services of similar acuity for Medicaid "
        "community engagement"
    )
    documentation = (
        "Whether the person is granted the optional Medicaid community "
        "engagement short-term hardship exception (42 CFR 435.555(d)(1)) "
        "because they receive inpatient hospital, nursing facility, ICF/IID, "
        "or inpatient psychiatric hospital services, or other services of "
        "similar acuity. The exception is a state option that the person (or "
        "someone acting on their behalf) must request; this input asserts "
        "that the state has elected the option and granted the exception. It "
        "lets household situations represent the circumstance since survey "
        "data lack a hospital utilization signal, and defaults to false, so "
        "it does not affect microsimulation results."
    )
    definition_period = YEAR
    default_value = False
    reference = (
        "https://www.govinfo.gov/content/pkg/FR-2026-06-03/pdf/2026-11094.pdf#page=126",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/cib12082025.pdf#page=6",
    )

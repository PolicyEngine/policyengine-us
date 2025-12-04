from policyengine_us.model_api import *


class is_ca_medicaid_continuous_coverage_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for California Medicaid continuous coverage"
    definition_period = YEAR
    reference = [
        "https://calmatters.org/health/2025/05/newsom-proposes-to-freeze-medi-cal-enrollment-for-undocumented-immigrants/",
    ]
    documentation = """
    California's 2026 enrollment freeze for undocumented immigrants only
    affects new enrollments. Existing enrollees retain their coverage.

    This variable allows existing Medi-Cal enrollees (indicated by
    is_on_medicaid = true) to remain eligible even if they would not
    qualify under the new 2026 rules.
    """
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        on_medicaid = person("is_on_medicaid", period)
        undocumented = (
            person("immigration_status", period)
            == person(
                "immigration_status", period
            ).possible_values.UNDOCUMENTED
        )
        # Continuous coverage applies to undocumented immigrants who are
        # already on Medicaid - they can retain coverage after the freeze
        return on_medicaid & undocumented

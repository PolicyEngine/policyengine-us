from policyengine_us.model_api import *


class is_ca_medicaid_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for California Medi-Cal without satisfactory immigration status"
    definition_period = YEAR
    reference = (
        "https://california.public.law/codes/welfare_and_institutions_code_section_14007.8",
    )
    documentation = """
    California Welfare and Institutions Code Section 14007.8 provides
    state-funded Medi-Cal to individuals without satisfactory immigration
    status based on age brackets. Starting January 1, 2026, new enrollments
    for adults 19+ are frozen, but existing enrollees retain coverage.
    """
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.chhs
        age = person("age", period)
        pregnant = person("is_pregnant", period)
        # Standard eligibility based on age or pregnancy
        standard_eligible = (
            p.eligible_regardless_of_immigration_status.calc(age) | pregnant
        )
        # Continuous coverage only applies after enrollment freeze
        if p.medi_cal_enrollment_freeze.in_effect:
            receives_medicaid = person("receives_medicaid", period)
            # Section 14007.8 is specifically for undocumented immigrants
            immigration_status = person("immigration_status", period)
            undocumented = (
                immigration_status
                == immigration_status.possible_values.UNDOCUMENTED
            )
            continuous_coverage = receives_medicaid & undocumented
            return standard_eligible | continuous_coverage
        return standard_eligible

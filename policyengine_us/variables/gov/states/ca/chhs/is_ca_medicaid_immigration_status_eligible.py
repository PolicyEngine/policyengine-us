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
    for adults 19+ are frozen for certain statuses (undocumented), but:
    - Existing enrollees retain coverage (continuous coverage)
    - DACA/TPS holders are NOT affected by the freeze
    - After October 2026, refugees/asylees losing federal coverage are
      picked up by CA state-funded coverage
    """
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.chhs
        immigration_status = person("immigration_status", period)
        immigration_status_str = immigration_status.decode_to_str()

        # Check if person has a CA state-funded eligible immigration status
        is_ca_state_funded_status = np.isin(
            immigration_status_str, p.ca_state_funded_immigration_statuses
        )

        age = person("age", period)
        pregnant = person("is_pregnant", period)
        # Standard eligibility based on age or pregnancy
        standard_eligible = (
            p.eligible_regardless_of_immigration_status.calc(age) | pregnant
        )

        # Enrollment freeze logic (effective January 1, 2026)
        if p.medi_cal_enrollment_freeze.in_effect:
            # Check if person's status is affected by the freeze
            is_freeze_affected = np.isin(
                immigration_status_str,
                p.medi_cal_enrollment_freeze.affected_statuses,
            )
            receives_medicaid = person("receives_medicaid", period)

            # Freeze-affected (UNDOCUMENTED): standard age eligibility OR
            #   continuous coverage (already enrolled)
            # Not freeze-affected (DACA/TPS/others): always eligible
            #   (Health4All covered all ages by 2024, freeze doesn't apply)
            return is_ca_state_funded_status & where(
                is_freeze_affected,
                standard_eligible | receives_medicaid,
                True,
            )

        return is_ca_state_funded_status & standard_eligible

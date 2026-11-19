from policyengine_us.model_api import *


class is_ca_medicaid_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for California Medi-Cal without satisfactory immigration status"
    definition_period = YEAR
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=14007.8.&lawCode=WIC",
        "https://www.ebudget.ca.gov/2015-16/pdf/Revised/BudgetSummary/HealthandHumanServices.pdf#page=1",
        "https://smcgov.org/media/63316/download#page=2",
    )
    documentation = """
    California Welfare and Institutions Code Section 14007.8 provides
    state-funded Medi-Cal to individuals without satisfactory immigration
    status based on age brackets. The formula applies the schedule in
    eligible_regardless_of_immigration_status to undocumented residents,
    the one in eligible_with_daca to DACA recipients and the one in
    eligible_with_tps to TPS holders. DACA recipients qualify at every age
    through permanent residence under color of law (PRUCOL), which
    Medi-Cal counts as a satisfactory immigration status, not through
    Section 14007.8. This
    variable is YEAR-defined and reads each schedule at January 1. So the
    expansion to children that starts May 1, 2016 applies in the model from
    2017, and the expansion to ages 50 and over that starts May 1, 2022
    applies from 2023. Starting January 1, 2026, new enrollments
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
        # Undocumented residents follow the Section 14007.8 age schedule,
        # DACA recipients a schedule that covers every age, and TPS holders
        # their own. The formula names each status it covers: a status added
        # to ca_state_funded_immigration_statuses gets false until this
        # formula names it and gives it a schedule.
        statuses = immigration_status.possible_values
        undocumented = immigration_status == statuses.UNDOCUMENTED
        daca = immigration_status == statuses.DACA
        tps = immigration_status == statuses.TPS
        status_eligible = is_ca_state_funded_status & (undocumented | daca | tps)
        age_eligible = select(
            [undocumented, daca, tps],
            [
                p.eligible_regardless_of_immigration_status.calc(age),
                p.eligible_with_daca.calc(age),
                p.eligible_with_tps.calc(age),
            ],
            default=False,
        )
        # Standard eligibility based on age or pregnancy
        standard_eligible = age_eligible | pregnant

        # Enrollment freeze logic (effective January 1, 2026)
        if p.medi_cal_enrollment_freeze.in_effect:
            # Check if person's status is affected by the freeze
            is_freeze_affected = np.isin(
                immigration_status_str,
                p.medi_cal_enrollment_freeze.affected_statuses,
            )
            current_medicaid_coverage = person("receives_medicaid", period) | person(
                "has_medicaid_health_coverage_at_interview", period
            )

            # Freeze-affected (UNDOCUMENTED): standard age eligibility OR
            #   continuous coverage (already enrolled)
            # Not freeze-affected (DACA, TPS): always eligible. The freeze
            #   names neither status.
            return status_eligible & where(
                is_freeze_affected,
                standard_eligible | current_medicaid_coverage,
                True,
            )

        return status_eligible & standard_eligible

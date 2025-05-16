from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person.occupation import (
    Occupation,
)


class is_eligible_for_fsla_overtime_protection(Variable):
    value_type = bool
    entity = Person
    label = "is eligible for overtime pay"
    reference = "https://www.law.cornell.edu/cfr/text/29/541.600"
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.income.exemption.overtime
        occupation = person("occupation", period)
        is_paid_hourly = person("is_paid_hourly", period)
        employment_income = person("employment_income", period)
        weekly_employment_income = employment_income / WEEKS_IN_YEAR

        occupation_exemptions = p.occupation_exemptions_before_salary
        is_occupation_exempt = np.zeros_like(occupation, dtype=bool)
        for enum_val in Occupation:
            if enum_val.value in occupation_exemptions:
                is_occupation_exempt = np.where(
                    occupation == enum_val, True, is_occupation_exempt
                )

        # Special case for computer science occupation due to different salary threshold
        is_computer_exempt = (
            (occupation == Occupation.COMPUTER_SCIENCE)
            & (not is_paid_hourly)
            & (
                weekly_employment_income / p.hours_threshold
                >= p.computer_salary_threshold
            )
        )

        # HCE exemption - highly compensated employees regardless of occupation
        is_hce_exempt = (employment_income >= p.hce_salary_threshold) & (
            not is_paid_hourly
        )

        # Xxempt occupations regardless of salary or payment method
        is_always_exempt = (occupation == Occupation.MILITARY) | (
            occupation == Occupation.NEVER_WORKED
        )

        # Exempt occupations with basis salary test
        is_standard_exempt = (
            is_occupation_exempt
            & (not is_paid_hourly)
            & (weekly_employment_income >= p.salary_basis_threshold)
        )

        # If any exemption applies, worker is not eligible for overtime protection
        is_exempt = (
            is_hce_exempt
            | is_computer_exempt
            | is_standard_exempt
            | is_always_exempt
        )

        # Return True if eligible for overtime protection, False if exempt
        return ~is_exempt

from policyengine_us.model_api import *


class is_eligible_for_fsla_overtime_protection(Variable):
    value_type = bool
    entity = Person
    label = "is eligible for overtime pay"
    reference = "https://www.law.cornell.edu/cfr/text/29/541.600 ; https://www.law.cornell.edu/uscode/text/29/213"
    definition_period = YEAR

    def formula_2023(person, period, parameters):
        p = parameters(period).gov.irs.income.exemption.overtime
        is_paid_hourly = person("is_paid_hourly", period)
        employment_income = person("employment_income", period)
        weekly_employment_income = employment_income / WEEKS_IN_YEAR

        # Special case for computer science occupation due to different salary threshold
        is_computer_exempt = (
            person("is_computer_scientist", period)
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

        # Exempt occupations regardless of salary or payment method
        is_always_exempt = person("is_military", period) | person(
            "has_never_worked", period
        )

        # Exempt occupations with basis salary test
        is_standard_exempt = (
            (
                person("is_executive_administrative_professional", period)
                | person("is_farmer_fisher", period)
            )
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

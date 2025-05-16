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

        # To be eligible for overtime pay, a person must be paid hourly and work more than 40 hours a week
        # a person must not be employed "in a bona fide executive, administrative, or professional (EAP) capacity" or in the fishing and farming industries (duties test)
        # or a person must be paid a salary and work more than 40 hours a week, with a basis salary under the threshold (salary test)

        # a person may be a highly compensated employee (HCE) and thus become ineligible for overtime pay even if they do not pass the duties test

        # a few occupations are not eligible under any circumstances: military,clergy

        # Return True if eligible for overtime protection, False if exempt
        return select(
            [
                (employment_income >= p.hce_salary_threshold)
                & (not is_paid_hourly),
                (occupation == Occupation.COMPUTER_SCIENCE)
                & (not is_paid_hourly)
                & (
                    weekly_employment_income / p.hours_threshold
                    >= p.computer_salary_threshold
                ),
                (occupation == Occupation.MANAGEMENT_BUSINESS_FINANCIAL)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.MANAGEMENT_INFRASTRUCTURE)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.OTHER_MANAGERS)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.BUSINESS_OPERATIONS)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.ACCOUNTING)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.FINANCE)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.MATH_SCIENCE)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.ARCHITECTURE)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.SURVEYING)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.ENGINEERING_TECH)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.EARTH_SCIENCE)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.ECONOMICS)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.SOCIAL_SCIENCE)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.HEALTH_SAFETY)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.LEGAL_PRACTICE)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.LEGAL_SUPPORT)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.NURSING_THERAPY)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.VETERINARY)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.HEALTH_TECHNICIANS)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.HEALTHCARE_SUPPORT)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.PROTECTIVE_SUPERVISORS)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.HOUSEKEEPING_SUPERVISORS)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.PERSONAL_CARE_SUPERVISORS)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.SALES_SUPERVISORS)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.SALES)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.ADMIN_SUPPORT)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.FARMING_FORESTRY)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.CONSTRUCTION_SUPERVISORS)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.TRANSPORT_SUPERVISORS)
                & (not is_paid_hourly)
                & (weekly_employment_income >= p.salary_basis_threshold),
                (occupation == Occupation.MILITARY),
                (occupation == Occupation.NEVER_WORKED),
            ],
            [
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
            default=True,
        )

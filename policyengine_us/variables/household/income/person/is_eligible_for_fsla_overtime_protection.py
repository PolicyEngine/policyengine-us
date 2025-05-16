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
    default_value = True

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.income.exemption.overtime
        occupation = person("occupation", period)
        is_paid_hourly = person("is_paid_hourly", period)
        weekly_employment_income = (
            person("employment_income", period) / WEEKS_IN_YEAR
        )

        # To be eligible for overtime pay, a person must be paid hourly and work more than 40 hours a week
        # a person must not be employed "in a bona fide executive, administrative, or professional (EAP) capacity" or in the fishing and farming industries (duties test)
        # or a person must be paid a salary and work more than 40 hours a week, with a basis salary under the threshold (salary test)

        # a person may be a highly compensated employee (HCE) and thus become ineligible for overtime pay even if they do not pass the duties test
        if (
            person("employment_income", period) >= p.hce_salary_threshold
            and not is_paid_hourly
        ):
            return False

        if (
            occupation == Occupation.MANAGEMENT_BUSINESS_FINANCIAL
            and not is_paid_hourly
        ):
            if weekly_employment_income > p.salary_basis_threshold:
                return False
            return False
        elif (
            occupation == Occupation.PROFESSIONAL_RELATED
            and not is_paid_hourly
        ):
            if weekly_employment_income > p.salary_basis_threshold:
                return False
        elif (
            occupation == Occupation.OFFICE_ADMINISTRATIVE
            and not is_paid_hourly
        ):
            if weekly_employment_income > p.salary_basis_threshold:
                return False
        elif (
            occupation == Occupation.FARMING_FISHING_FORESTRY
            and not is_paid_hourly
        ):
            if weekly_employment_income > p.salary_basis_threshold:
                return False
        # a few occupations are not eligible under any circumstances: military,clergy,
        elif occupation == Occupation.MILITARY:
            return False

        return True

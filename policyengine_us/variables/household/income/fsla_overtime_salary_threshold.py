from policyengine_us.model_api import *
from policyengine_us.variables.household.income.person.fsla_overtime_occupation_exemption_category import (
    OvertimeExemptionCategory,
)


class fsla_overtime_salary_threshold(Variable):
    value_type = float
    entity = Person
    label = "FSLA applicable salary threshold to determine eligibility for overtime pay"
    reference = "https://www.law.cornell.edu/cfr/text/29/541.600"
    definition_period = YEAR
    unit = USD

    def formula_2014(person, period, parameters):
        p = parameters(period).gov.irs.income.exemption.overtime
        category = person(
            "fsla_overtime_occupation_exemption_category", period
        )

        # Initialize all thresholds to HCE - this applies to everyone by default
        # except for those who are always exempt (military, never worked)
        threshold = np.full_like(category, p.hce_salary_threshold, dtype=float)

        # Special category thresholds (these override HCE if they're lower)
        is_computer = category == OvertimeExemptionCategory.COMPUTER_SCIENTIST
        is_exec_admin = (
            category == OvertimeExemptionCategory.EXECUTIVE_ADMINISTRATIVE
        )
        is_farmer_fisher = category == OvertimeExemptionCategory.FARMER_FISHER

        threshold = np.where(
            is_computer,
            np.minimum(
                p.computer_salary_threshold
                * WEEKS_IN_YEAR
                * p.hours_threshold,
                p.hce_salary_threshold,
            ),
            threshold,
        )
        threshold = np.where(
            is_exec_admin | is_farmer_fisher,
            np.minimum(
                p.salary_basis_threshold * WEEKS_IN_YEAR,
                p.hce_salary_threshold,
            ),
            threshold,
        )

        # Always exempt categories have threshold of 0 (any income means exempt)
        is_always_exempt = (category == OvertimeExemptionCategory.MILITARY) | (
            category == OvertimeExemptionCategory.NEVER_WORKED
        )
        threshold = np.where(is_always_exempt, 0, threshold)

        return threshold

from policyengine_us.model_api import *


class is_chip_fcep_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Pregnant person eligible for CHIP through FCEP"
    documentation = "Determines if a pregnant person is eligible for the Children's Health Insurance Program through the Family Coverage Extension Program"
    definition_period = YEAR
    reference = (
        "https://www.kff.org/affordable-care-act/state-indicator/medicaid-and-chip-income-eligibility-limits-for-pregnant-women-as-a-percent-of-the-federal-poverty-level",
    )

    def formula(person, period, parameters):
        # Get state code
        state_code = person.household("state_code", period)

        # Check pregnancy status
        is_pregnant = person("is_pregnant", period)

        # Check if state offers FCEP program for pregnant women
        p = parameters(period).gov.hhs.chip.fcep
        income_limit = p.income_limit[state_code]

        state_has_fcep = income_limit > 0

        # Check immigration status eligibility
        istatus = person("immigration_status", period)
        undocumented = istatus == istatus.possible_values.UNDOCUMENTED
        immigration_eligible = ~undocumented

        # Check income eligibility
        # CHIP is for pregnant women who make too much for Medicaid but below CHIP limits
        # First, check if not eligible for Medicaid
        medicaid_eligible = person("is_medicaid_eligible", period)

        # Check if family income is below CHIP threshold
        # Use medicaid_income_level as the income measure
        income_ratio = person("medicaid_income_level", period)
        income_eligible = income_ratio <= income_limit

        return (
            is_pregnant
            & state_has_fcep
            & immigration_eligible
            & ~medicaid_eligible
            & income_eligible
        )

from policyengine_us.model_api import *


class is_chip_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Child eligible for CHIP"
    documentation = "Determines if a child is eligible for the Children's Health Insurance Program"
    definition_period = YEAR
    reference = (
        "https://www.ssa.gov/OP_Home/ssact/title21/2110.htm",
        "https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-childrens-health-insurance-program-basic-health-program-eligibility-levels",
    )

    def formula(person, period, parameters):
        # Get state code
        state_code = person.household("state_code", period)

        # Check age eligibility
        age = person("age", period)
        p = parameters(period).gov.hhs.chip.child

        is_age_eligible = age < p.max_age

        # Check if state offers CHIP program for children
        income_limit = p.income_limit[state_code]
        state_has_chip = income_limit > 0

        # Check immigration status eligibility
        istatus = person("immigration_status", period)
        undocumented = istatus == istatus.possible_values.UNDOCUMENTED
        immigration_eligible = ~undocumented

        # Check income eligibility
        # CHIP is for children who make too much for Medicaid but below CHIP limits
        # First, check if not eligible for Medicaid
        medicaid_eligible = person("is_medicaid_eligible", period)

        # Check if family income is below CHIP threshold
        # Use medicaid_income_level as the income measure
        income_ratio = person("medicaid_income_level", period)
        income_eligible = income_ratio <= income_limit

        return (
            is_age_eligible
            & state_has_chip
            & immigration_eligible
            & ~medicaid_eligible
            & income_eligible
        )

from policyengine_us.model_api import *


class is_chip_eligible_standard_pregnant_person(Variable):
    value_type = bool
    entity = Person
    label = "Pregnant person eligible for standard CHIP"
    documentation = "Determines if a pregnant person is eligible for the standard Children's Health Insurance Program"
    definition_period = YEAR
    reference = (
        "https://www.ssa.gov/OP_Home/ssact/title21/2110.htm",
        "https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-childrens-health-insurance-program-basic-health-program-eligibility-levels",
    )

    def formula(person, period, parameters):
        # Get state code
        state_code = person.household("state_code", period)

        # Check pregnancy status
        is_pregnant = person("is_pregnant", period)

        # Check if state offers CHIP program for pregnant women
        p = parameters(period).gov.hhs.chip.pregnant
        income_limit = p.income_limit[state_code]

        state_has_pregnant_chip = income_limit > 0

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
            & state_has_pregnant_chip
            & immigration_eligible
            & ~medicaid_eligible
            & income_eligible
        )

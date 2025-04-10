from policyengine_us.model_api import *


class is_chip_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for CHIP"
    documentation = "Determines if a person is eligible for the Children's Health Insurance Program"
    definition_period = YEAR
    reference = (
        "https://www.ssa.gov/OP_Home/ssact/title21/2110.htm",
        "https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-childrens-health-insurance-program-basic-health-program-eligibility-levels",
    )

    def formula(person, period, parameters):
        # CHIP eligibility is based on being either an eligible child or pregnant woman
        is_eligible_child = person("is_chip_eligible_child", period)
        is_eligible_pregnant = person("is_chip_eligible_pregnant", period)

        # Check immigration status eligibility - redundant with child/pregnant checks but included for clarity
        istatus = person("immigration_status", period)
        undocumented = istatus == istatus.possible_values.UNDOCUMENTED
        immigration_eligible = ~undocumented

        # A person is eligible if they qualify under either category and have eligible immigration status
        return immigration_eligible & (
            is_eligible_child | is_eligible_pregnant
        )

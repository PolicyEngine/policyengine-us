from policyengine_us.model_api import *


class is_chip_eligible_pregnant(Variable):
    value_type = bool
    entity = Person
    label = "Pregnant person eligible for CHIP"
    documentation = "Determines if a pregnant person is eligible for the Children's Health Insurance Program through either the standard pregnant pathway or FCEP"
    definition_period = YEAR
    reference = (
        "https://www.ssa.gov/OP_Home/ssact/title21/2110.htm",
        "https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-childrens-health-insurance-program-basic-health-program-eligibility-levels",
        "https://www.kff.org/affordable-care-act/state-indicator/medicaid-and-chip-income-eligibility-limits-for-pregnant-women-as-a-percent-of-the-federal-poverty-level",
    )

    def formula(person, period, parameters):
        # A person is eligible for CHIP as pregnant if they qualify through either
        # the standard pregnant pathway or the FCEP pathway

        # Check standard pregnant pathway eligibility
        standard_eligible = person(
            "is_chip_eligible_standard_pregnant_person", period
        )

        # Check FCEP pathway eligibility
        fcep_eligible = person("is_chip_fcep_eligible_person", period)

        # Eligible if either pathway qualifies
        return standard_eligible | fcep_eligible

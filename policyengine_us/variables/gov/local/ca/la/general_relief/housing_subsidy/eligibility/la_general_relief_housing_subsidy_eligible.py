from policyengine_us.model_api import *


class la_general_relief_housing_subsidy_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible for the Los Angeles County General Relief Housing Subsidy"
    )
    definition_period = YEAR
    # Person has to be a resident of LA County
    defined_for = "la_general_relief_eligible"
    reference = "https://dpss.lacounty.gov/en/cash/gr/housing.html"

    def formula(spm_unit, period, parameters):
        household = spm_unit.household
        # Person has to experience homelessness
        # Considering people who are about to loose housing as homeless
        homeless = household("is_homeless", period)
        # Person has to be aprt of other specific programs to be eligible for the housing subsidy
        program_eligible = spm_unit(
            "la_general_relief_housing_subsidy_program_eligible", period
        )
        # Person or couple can not have dependents
        dependents = add(spm_unit, period, ["tax_unit_dependents"])
        # General relief cannot be under the rent subsidy amounts
        gr_amount_eligible = spm_unit(
            "la_general_relief_housing_subsidy_base_amount_eligible", period
        )
        return (
            program_eligible
            & homeless
            & (dependents == 0)
            & gr_amount_eligible
        )

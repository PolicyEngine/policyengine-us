from policyengine_us.model_api import *


class PellGrantEligibilityType(Enum):
    MAXIMUM = "maximum"
    MINIMUM = "minimum"
    INELIGIBLE = "ineligible"


class pell_grant_eligibility_type(Variable):
    value_type = Enum
    possible_values = PellGrantEligibilityType
    default_value = PellGrantEligibilityType.INELIGIBLE
    entity = Person
    definition_period = YEAR
    label = "Maximum, minimum, or ineligible for Pell Grant"

    def formula(person, period, parameters):
        agi = person.tax_unit("adjusted_gross_income", period)
        # FPG from the prior-prior year.
        fpg = person.tax_unit("tax_unit_fpg", period.offset(-2, "year"))
        fpg_percent = agi / fpg

        max_limit = person("pell_grant_max_fpg_percent_limit", period)
        min_limit = person("pell_grant_min_fpg_percent_limit", period)

        return select(
            [fpg_percent <= max_limit, fpg_percent <= min_limit],
            [
                PellGrantEligibilityType.MAXIMUM,
                PellGrantEligibilityType.MINIMUM,
            ],
            default=PellGrantEligibilityType.INELIGIBLE,
        )

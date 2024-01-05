from policyengine_us.model_api import *


class OregonWFHDCEligibilityCategory(Enum):
    age_under_3 = "age_under_3"
    age_3_to_6 = "age_3_to_6"
    age_6_to_13 = "age_6_to_13"
    disabled_13_to_18 = "disabled_13_to_18"
    disabled_18_and_over = "disabled_18_and_over"
    NONE = "Empty String"


class or_wfhdc_eligibility_category(Variable):
    value_type = Enum
    possible_values = OregonWFHDCEligibilityCategory
    entity = TaxUnit
    label = "Oregon working family household and dependent care credit percentage table column"
    unit = USD
    definition_period = YEAR
    defined_for = "or_wfhdc_eligible"
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-wfhdc-tb_101-458_2021.pdf#page=1"
    default_value = OregonWFHDCEligibilityCategory.NONE

    def formula(tax_unit, period, parameters):
        # Column determined by age of youngest child and whether they have a disability.

        # Get parameters
        p = (
            parameters(period)
            .gov.states["or"]
            .tax.income.credits.wfhdc.age_range
        )
        # Get the age of the youngest qualifying child.
        person = tax_unit.members
        age = person("age", period)
        min_age = tax_unit.min(age)

        # Determine if the youngest qualifying individual is disabled.
        # The household has at least one qualifying individual because they are WFHDC eligible.
        disabled = person("is_disabled", period)
        youngest_and_disabled = (age == min_age) & disabled

        # This will be true if any child with the lowest age is disabled.
        youngest_is_disabled = tax_unit.sum(youngest_and_disabled) > 0
        conditions = [
            min_age < p.youngest,
            min_age < p.young,
            min_age < p.old,
            (min_age < p.oldest) & youngest_is_disabled,
            youngest_is_disabled,
        ]
        values = [
            OregonWFHDCEligibilityCategory.age_under_3,
            OregonWFHDCEligibilityCategory.age_3_to_6,
            OregonWFHDCEligibilityCategory.age_6_to_13,
            OregonWFHDCEligibilityCategory.disabled_13_to_18,
            OregonWFHDCEligibilityCategory.disabled_18_and_over,
        ]

        return select(
            conditions, values, default=OregonWFHDCEligibilityCategory.NONE
        )

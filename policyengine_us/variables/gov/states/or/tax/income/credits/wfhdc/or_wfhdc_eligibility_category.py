from policyengine_us.model_api import *


class OregonWFHDCEligibilityCategory(Enum):
    YOUNGEST = "Youngest"  # under 3 years old
    YOUNG = "Young"  # between 3 and 6 years old
    OLD = "Old"  # between 6 and 13 years old
    DISABLED_TEENS = "Disabled teenagers"  # disabled teenagers that are between 13 and 18 years old
    DISABLED_ADULTS = (
        "Disabled adults"  # disabled adults that are over 18 years old
    )
    NONE = "None"


class or_wfhdc_eligibility_category(Variable):
    value_type = Enum
    possible_values = OregonWFHDCEligibilityCategory
    entity = TaxUnit
    label = "Oregon working family household and dependent care credit percentage table column"
    definition_period = YEAR
    defined_for = "or_wfhdc_eligible"
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-wfhdc-tb_101-458_2021.pdf#page=1"
    default_value = OregonWFHDCEligibilityCategory.NONE

    def formula(tax_unit, period, parameters):
        # Column determined by age of youngest child and whether they have a disability.

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
        disabled_rank = person.get_rank(tax_unit, age, disabled)
        youngest_and_disabled = disabled_rank == -1

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
            OregonWFHDCEligibilityCategory.YOUNGEST,
            OregonWFHDCEligibilityCategory.YOUNG,
            OregonWFHDCEligibilityCategory.OLD,
            OregonWFHDCEligibilityCategory.DISABLED_TEENS,
            OregonWFHDCEligibilityCategory.DISABLED_ADULTS,
        ]
        return select(
            conditions, values, default=OregonWFHDCEligibilityCategory.NONE
        )

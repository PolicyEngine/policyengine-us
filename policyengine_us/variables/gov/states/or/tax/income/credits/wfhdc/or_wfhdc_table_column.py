from policyengine_us.model_api import *


class OrTableColumn(Enum):
    age_under_3 = "age_under_3"
    age_3_to_6 = "age_3_to_6"
    age_6_to_13 = "age_6_to_13"
    disabled_13_to_18 = "disabled_13_to_18"
    disabled_18_and_over = "disabled_18_and_over"
    NONE = "Empty String"  


class or_wfhdc_table_column(Variable):
    value_type = Enum
    possible_values = OrTableColumn
    entity = TaxUnit
    label = "Oregon working family household and dependent care credit percentage table column"
    unit = USD
    definition_period = YEAR
    defined_for = "or_wfhdc_eligible"
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-wfhdc-tb_101-458_2021.pdf#page=1"
    default_value = OrTableColumn.NONE

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
        min_age = age.min()

        # Determine if the youngest qualifying individual is disabled.
        # The household has at least one qualifying individual because they are WFHDC eligible.
        disabled = person("is_disabled", period)
        youngest_and_disabled = (age == min_age) & disabled

        # This will be true if any child with the lowest age is disabled.
        youngest_is_disabled = youngest_and_disabled.sum() > 0
        conditions = [
            min_age < p.three,
            min_age < p.six,
            min_age < p.thirteen,
            (min_age < p.eighteen) & youngest_is_disabled,
            youngest_is_disabled,
        ]
        values = [
            OrTableColumn.age_under_3,
            OrTableColumn.age_3_to_6,
            OrTableColumn.age_6_to_13,
            OrTableColumn.disabled_13_to_18,
            OrTableColumn.disabled_18_and_over,
        ]

        return select(conditions, values, default=OrTableColumn.NONE)

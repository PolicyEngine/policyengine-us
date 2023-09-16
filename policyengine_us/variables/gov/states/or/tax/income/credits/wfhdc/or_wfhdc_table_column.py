from policyengine_us.model_api import *


class or_wfhdc_table_column(Variable):
    value_type = str
    entity = TaxUnit
    label = "Oregon WFHDC percentage table column"
    unit = USD
    definition_period = YEAR
    defined_for = "or_wfhdc_eligible"
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-wfhdc-tb_101-458_2022.pdf"
    default_value = ""

    def formula(tax_unit, period, parameters):
        # Column determined by age/disability of youngest child.

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
            min_age < 3,
            min_age < 6,
            min_age < 13,
            (min_age < 18) & youngest_is_disabled,
            youngest_is_disabled,
        ]
        values = [
            "age_under_3",
            "age_3_to_6",
            "age_6_to_13",
            "disabled_13_to_18",
            "disabled_18_and_over",
        ]

        return select(conditions, values, default="")

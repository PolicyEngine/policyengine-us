from policyengine_us.model_api import *


class or_wfhdc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon WFHDC"
    unit = USD
    definition_period = YEAR
    defined_for = "or_wfhdc_income_eligible"
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-wfhdc-tb_101-458_2022.pdf"

    def formula(tax_unit, period, parameters):
        # Get the parameter tree for WFHDC.
        p = parameters(period).gov.states["or"].tax.income.credits.wfhdc

        # Get the household size.
        household_size = tax_unit("tax_unit_size", period)

        # Get the household income, considered the larger of federal and Oregon AGI.
        federal_agi = tax_unit("adjusted_gross_income", period)
        or_agi = tax_unit("or_income_after_subtractions", period)
        household_income = max_(federal_agi, or_agi)

        # Get the age of the youngest qualifying child.
        person = tax_unit.members
        age = person("age", period)
        min_age = min_(age)
        # min_age = 5

        # how should we located the youngest child?

        # Determine if the youngest child is disabled.
        # disabled = False
        # min_age = min_(person("is_disabled", period))
        disabled = person("is_disabled", period)

        # Determine if youngest child is disabled.
        # Assume that the household has a child because they are WFHDC eligible.
        youngest_and_disabled = (age == min_age) & disabled
        youngest_is_disabled = sum_(youngest_and_disabled) > 0

        # # Get the corresponding row from WFHDC tables.
        percentage = select(
            [
                min_age < 3,
                min_age < 6,
                min_age < 13,
                (min_age < 18) & youngest_is_disabled,
                youngest_is_disabled,
            ],
            [
                p.table_threshold["household_size_2"].calc(household_income)[
                    "not_disabled_under3"
                ],
                p.table_threshold["household_size_2"].calc(household_income)[
                    "not_disabled_3_to_6"
                ],
                p.table_threshold["household_size_2"].calc(household_income)[
                    "not_disabled_6_to_13"
                ],
                p.table_threshold["household_size_2"].calc(household_income)[
                    "disabled_13_to_18"
                ],
                p.table_threshold["household_size_2"].calc(household_income)[
                    "disabled_above_18"
                ],
            ],
            default_value=0,
        )

        # Get the federal CDCC value.
        cdcc = tax_unit("cdcc", period)

        # Return the share of federal CDCC matched by Oregon.
        return cdcc * percentage

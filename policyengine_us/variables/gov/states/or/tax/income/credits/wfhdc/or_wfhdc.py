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
        min_age = min_(person("age", period))
        # min_age = 5

        # how should we located the youngest child?

        # Determine if the youngest child is disabled.
        # disabled = False
        disabled = person("is_disabled", period)
        min_age = min_(person("is_disabled", period))

        # # Get the corresponding row from WFHDC tables.
        percentage_disabled = select(
            [min_age < 3, min_age < 6, min_age < 13],
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

        percentage_not_disabled = select(
            [min_age < 3, min_age < 6, min_age < 13],
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
            ],
            default_value=0,
        )

        percentage = where(
            disabled, percentage_disabled, percentage_not_disabled
        )
        # Get the federal CDCC value.
        cdcc = tax_unit("cdcc", period)

        # Return the share of federal CDCC matched by Oregon.
        return cdcc * percentage_not_disabled

        # cor_household_size = p.corresponding_row[household_size]
        # cor_row = cor_household_size.calc(household_income)

        # Get the corresponding credit percentage from WFHDC tables

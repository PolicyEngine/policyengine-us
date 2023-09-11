from policyengine_us.model_api import *


class or_wfhdc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon WFHDC"
    unit = USD
    definition_period = YEAR
    defined_for = "or_wfhdc_eligible"
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-wfhdc-tb_101-458_2022.pdf"

    def formula(tax_unit, period, parameters):
        # Get the parameter tree for WFHDC.
        p = parameters(period).gov.states["or"].tax.income.credits.wfhdc

        # Get the household size.
        household_size = tax_unit("tax_unit_size", period)[0]

        # Get the household income, considered the larger of federal and Oregon AGI.
        federal_agi = tax_unit("adjusted_gross_income", period)
        or_agi = tax_unit("or_income_after_subtractions", period)
        household_income = max_(federal_agi, or_agi)

        # Get the age of the youngest qualifying child.
        person = tax_unit.members
        age = person("age", period)
        min_age = age.min()

        # Determine if the youngest child is disabled.
        # Assume that the household has a child because they are WFHDC eligible.
        disabled = person("is_disabled", period)
        youngest_and_disabled = (age == min_age) & disabled

        # This will be true if any child with the lowest age is disabled.
        youngest_is_disabled = youngest_and_disabled.sum() > 0

        hh_size_param_name = "household_size_" + str(household_size)

        conditions = [
            min_age < 3,
            min_age < 6,
            min_age < 13,
            (min_age < 18) & youngest_is_disabled,
            youngest_is_disabled,
        ]

        values = [
            p.table_threshold[hh_size_param_name]["age_under_3"].calc(
                household_income
            ),
            p.table_threshold[hh_size_param_name]["age_3_to_6"].calc(
                household_income
            ),
            p.table_threshold[hh_size_param_name]["age_6_to_13"].calc(
                household_income
            ),
            p.table_threshold[hh_size_param_name]["disabled_13_to_18"].calc(
                household_income
            ),
            p.table_threshold[hh_size_param_name]["disabled_above_18"].calc(
                household_income
            ),
        ]

        # Get the corresponding row from WFHDC tables.
        percentage = select(conditions, values)

        # Get the relevant expenses.
        expenses = tax_unit("cdcc_relevant_expenses", period)

        # Return the share of federal CDCC matched by Oregon.
        return expenses * percentage

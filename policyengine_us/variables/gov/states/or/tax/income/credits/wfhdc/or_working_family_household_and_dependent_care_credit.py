from policyengine_us.model_api import *


class or_working_family_household_and_dependent_care_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon working family household and dependent care credit"
    unit = USD
    definition_period = YEAR
    defined_for = "or_wfhdc_eligible"
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-wfhdc-tb_101-458_2022.pdf"

    def formula(tax_unit, period, parameters):
        # Get the parameter tree for WFHDC.
        p = parameters(period).gov.states["or"].tax.income.credits.wfhdc

        # Get the corresponding table letter for each household.
        income_category = tax_unit("or_wfhdc_income_category", period)

        # Get the corresponding table column for each household.
        eligibility_category = tax_unit(
            "or_wfhdc_eligibility_category", period
        )

        # Get the OR WFHDC percentage based on the table letter and column.
        match_percentage = p.match[income_category][eligibility_category]

        # Get the relevant expenses.
        expenses = tax_unit("or_cdcc_relevant_expenses", period)

        # Return the share of federal CDCC matched by Oregon.
        return expenses * match_percentage

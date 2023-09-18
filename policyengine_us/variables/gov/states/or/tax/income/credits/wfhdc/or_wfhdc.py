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

        # Get the corresponding table letter for each household.
        table_letter = tax_unit("or_wfhdc_table_letter", period)

        # Get the corresponding table column for each household.
        table_column = tax_unit("or_wfhdc_table_column", period)

        # Get the OR WFHDC percentage based on the table letter and column.
        percentage = p.table_threshold[table_letter][table_column]

        # Get the relevant expenses.
        expenses = tax_unit("cdcc_relevant_expenses", period)

        # Return the share of federal CDCC matched by Oregon.
        return expenses * percentage

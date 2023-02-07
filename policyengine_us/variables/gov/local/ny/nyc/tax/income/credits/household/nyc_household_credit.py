from policyengine_us.model_api import *


class nyc_household_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC Household Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        # First get their federal AGI.
        federal_agi = tax_unit("adjusted_gross_income", period)

        # Then get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the household credit part of the parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.household

        # Then get their number of dependents.
        n_dependents = tax_unit("tax_unit_count_dependents", period)

        # Calculate the flat amount that is regardless of dependent count.
        flat_amount = p.flat_amount[filing_status][federal_agi]

        # Calculuate the amount of credit per dependent.
        credit_per_dependent = p.amount_per_dependent[filing_status][federal_agi]

        # Calculate the total variable amount (based on number of dependents).
        variable_amount = n_dependents * credit_per_dependent

        # Return the total credit.
        return flat_amount + variable_amount

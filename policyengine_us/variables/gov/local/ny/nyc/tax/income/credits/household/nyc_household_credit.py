from policyengine_us.model_api import *
from policyengine_us.tools.general import select_filing_status_value


class nyc_household_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC Household Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        # First get their federal AGI.
        # Technically based on recomputed AGI, which deviates slightly from federal AGI.
        federal_agi = tax_unit("adjusted_gross_income", period)

        # Then get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the household credit part of the parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.household

        # Then get their number of people.
        tax_unit_size = tax_unit("tax_unit_size", period)

        # Create a dictionary of values for each filing status
        filing_status_values = {
            "single": p.flat_amount.calc(federal_agi, right=True),
            "separate": p.separate_per_dependent.calc(federal_agi, right=True)
            * tax_unit_size,
            # Joint, head of household, and surviving spouse use the same formula
            "joint": p.other_per_dependent.calc(federal_agi, right=True)
            * tax_unit_size,
            "head_of_household": p.other_per_dependent.calc(
                federal_agi, right=True
            )
            * tax_unit_size,
            "surviving_spouse": p.other_per_dependent.calc(
                federal_agi, right=True
            )
            * tax_unit_size,
        }

        return select_filing_status_value(
            filing_status,
            filing_status_values,
        )

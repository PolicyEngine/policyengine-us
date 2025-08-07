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
        # Technically based on recomputed AGI, which deviates slightly from federal AGI.
        federal_agi = tax_unit("adjusted_gross_income", period)

        # Then get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the household credit part of the parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.household

        # Then get their number of people.
        tax_unit_size = tax_unit("tax_unit_size", period)

        filing_statuses = filing_status.possible_values

        return select(
            [
                filing_status == filing_statuses.SINGLE,
                filing_status == filing_statuses.SEPARATE,
            ],
            [
                # Single filers get a flat amount.
                p.flat_amount.calc(federal_agi, right=True),
                # Separate filers get an amount for each person in the tax
                # unit, varying with AGI.
                p.separate_per_dependent.calc(federal_agi, right=True)
                * tax_unit_size,
            ],
            # Joint, head of household, and surviving spouse filers have a different
            # amount per person, varying with AGI.
            default=p.other_per_dependent.calc(federal_agi, right=True)
            * tax_unit_size,
        )

from openfisca_us.model_api import *


class ny_household_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY household credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (b)

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).states.ny.tax.income.credits.nonrefundable.household_credit
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        agi = tax_unit("adjusted_gross_income", period)
        single = filing_status == filing_statuses.SINGLE
        amount_single = p.single.calc(agi, right=True)  # "over...but not over"
        # TODO: Other filing statuses.
        return amount_single * single

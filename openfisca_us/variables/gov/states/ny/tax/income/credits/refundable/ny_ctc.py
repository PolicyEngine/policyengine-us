from openfisca_us.model_api import *


class ny_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY CTC"
    description = "New York's Empire State Child Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-1)

    def formula(tax_unit, period, parameters):
        in_ny = tax_unit.household("state_code_str", period) == "NY"
        p = parameters(period).states.ny.tax.income.credits.refundable.ctc
        # Qualifying children
        # Maximum of the minimum amount per child and the share of the federal credit.
        minimum = 
        ctc = tax_unit("child_tax_credit", period)
        
        tentative_nys_eic = eitc * rate
        household_credit = tax_unit("ny_household_credit", period)
        return in_ny * max_(0, tentative_nys_eic - household_credit)

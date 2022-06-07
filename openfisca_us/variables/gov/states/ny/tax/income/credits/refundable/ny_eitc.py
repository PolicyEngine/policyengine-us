from openfisca_us.model_api import *


class ny_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (d)

    def formula(tax_unit, period, parameters):
        eitc = tax_unit("earned_income_tax_credit", period)
        rate = parameters(period).states.ny.tax.income.credits.refundable.eitc
        tentative_nys_eic = eitc * rate
        household_credit = tax_unit("ny_household_credit", period)
        return tentative_nys_eic - household_credit

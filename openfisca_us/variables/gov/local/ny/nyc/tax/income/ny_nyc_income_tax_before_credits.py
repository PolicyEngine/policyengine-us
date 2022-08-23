from openfisca_us.model_api import *


class ny_nyc_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC income tax before credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        # determine if tax unit is in NYC
        county = tax_unit.household("county", period)
        counties = county.possible_values
        is_in_nyc = (
            (county == counties.NEW_YORK_COUNTY_NY)
            | (county == counties.KINGS_COUNTY_NY)
            | (county == counties.QUEENS_COUNTY_NY)
            | (county == counties.BRONX_COUNTY_NY)
            | (county == counties.RICHMOND_COUNTY_NY)
        )
        taxable_income = tax_unit("ny_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values

        rates = parameters(period).gov.local.ny.nyc.tax.income.rates
        single = rates.single
        joint = rates.joint
        hoh = rates.head_of_household
        widow = rates.widow
        separate = rates.separate

        return is_in_nyc * select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.WIDOW,
                filing_status == status.SEPARATE,
            ],
            [
                single.calc(taxable_income),
                joint.calc(taxable_income),
                hoh.calc(taxable_income),
                widow.calc(taxable_income),
                separate.calc(taxable_income),
            ],
        )

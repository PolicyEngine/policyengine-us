from policyengine_us.model_api import *


class ny_yonkers_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Yonkers income tax"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pit/file/nyc_yonkers_residents.htm"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.local.ny.yonkers.tax.income
        # Resident surcharge: a fraction of New York State net tax liability.
        resident = tax_unit.household("in_yonkers", period)
        ny_income_tax = tax_unit("ny_income_tax", period)
        resident_surcharge = (
            where(resident, ny_income_tax, 0) * p.resident_surcharge_rate
        )
        # Nonresident earnings tax: a flat rate on Yonkers-source wages.
        person = tax_unit.members
        nonresident_earnings = person("ny_yonkers_nonresident_earnings", period)
        nonresident_tax = (
            tax_unit.sum(max_(nonresident_earnings, 0)) * p.nonresident_rate
        )
        return resident_surcharge + nonresident_tax

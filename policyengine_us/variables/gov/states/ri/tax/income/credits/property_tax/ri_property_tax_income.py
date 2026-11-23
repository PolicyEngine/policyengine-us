from policyengine_us.model_api import *


class ri_property_tax_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island property tax credit income of a tax unit's members"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Income as R.I. Gen. Laws 44-33-3(7) defines it, for the members of "
        "one tax unit: federal adjusted gross income plus non-taxable income, "
        "with the business, rental, pass-through and capital losses and the "
        "section 911 amounts that federal AGI subtracts added back. "
        "ri_property_tax_household_income sums it over the household."
    )
    reference = (
        "http://webserver.rilegislature.gov/Statutes/TITLE44/44-33/44-33-3.htm",
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2026-01/2025%201040H_w.pdf#page=2",
    )
    defined_for = StateCode.RI
    adds = "gov.states.ri.tax.income.credits.property_tax.income_sources"

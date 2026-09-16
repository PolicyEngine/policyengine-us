from policyengine_us.model_api import *


class il_property_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois property tax rebate"
    unit = USD
    definition_period = YEAR
    defined_for = "il_property_tax_rebate_eligible"
    reference = "https://www.illinois.gov/news/release.html?releaseid=25425"

    def formula(tax_unit, period, parameters):
        # The 2022 Illinois Family Relief Plan paid a one-time property tax
        # rebate equal to the property tax credit the filer qualified for on
        # their 2021 return, capped at $300. Filers could claim it on Form
        # IL-1040-PTR even with no income tax liability, so it is based on the
        # potential (pre-liability-limitation) property tax credit -- 5% of
        # property tax paid -- not the applied credit.
        p = parameters(period).gov.states.il.tax.income.credits.property_tax_rebate
        property_tax_credit = tax_unit("il_property_tax_credit_potential", period)
        return min_(property_tax_credit, p.cap)

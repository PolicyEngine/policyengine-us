from policyengine_us.model_api import *


class nm_property_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico property tax rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf"
    defined_for = StateCode.NM
    defined_for = "nm_property_tax_rebate_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.tax.income.rebates.property_tax
        agi = tax_unit("nm_agi", period)
        # Get property tax paid by person
        ptax_owner = add(tax_unit, period, ["real_estate_taxes"])
        # Get person rent and multiply by 6%
        rent = add(tax_unit, period, ["rent"])
        rent_percent = rent * p.rate
        rent_and_ptax = ptax_owner + rent_percent
        # Get the maximum property tax liability
        max_liability = p.max_property_tax_liability.calc(agi)
        rebate = max_(0, rent_and_ptax - max_liability)
        # Cap is based on filing status
        filing_status = tax_unit("filing_status", period)
        return min_(rebate, p.cap[filing_status])

from policyengine_us.model_api import *


class nm_property_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico property tax rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503750/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsAgJQAaZNlKEIARUSFcAT2gBydRIiEwuBIuVrN23fpABlPKQBCagEoBRADKOAagEEAcgGFHE0jAAI2hSdjExIA"
    defined_for = StateCode.NM
    defined_for = "nm_property_tax_rebate_eligible"

    def formula(tax_unit, period, parameters):
        # Get property tax paid
        ptax_owner = add(tax_unit, period, ["real_estate_taxes"])
        # Get rent and multiply by 6%
        rent = add(tax_unit, period, ["rent"])
        p = parameters(period).gov.states.nm.tax.income.rebates.property_tax
        rent_percent = rent * p.rent_rate
        rent_and_ptax = ptax_owner + rent_percent
        # Get the maximum property tax liability
        agi = tax_unit("nm_modified_gross_income", period)
        max_liability = p.max_property_tax_liability.calc(agi, right=True)
        rebate = max_(0, rent_and_ptax - max_liability)
        # Maximum amount is based on filing status
        filing_status = tax_unit("filing_status", period)
        return min_(rebate, p.max_amount[filing_status])

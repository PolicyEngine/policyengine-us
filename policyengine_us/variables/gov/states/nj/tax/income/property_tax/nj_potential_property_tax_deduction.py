from policyengine_us.model_api import *


class nj_potential_property_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey potential property tax deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-3a-17/"
        "https://www.state.nj.us/treasury/taxation/pdf/other_forms/tgi-ee/2021/1040i.pdf#page=25"
    )
    defined_for = "nj_property_tax_deduction_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.deductions.property_tax

        # property_tax amount calculation follows NJ-1040 form Worksheet G
        rent = add(tax_unit, period, ["rent"])
        ptax = add(tax_unit, period, ["real_estate_taxes"])
        property_tax = ptax + rent * p.qualifying_rent_fraction

        # if filing separate but maintain same home, halve property_tax amount
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        cohabitating = tax_unit("cohabitating_spouses", period)
        property_tax = property_tax / (1 + separate * cohabitating)

        # limit property_tax amount
        limit = p.limit / (1 + separate * cohabitating)
        return min_(property_tax, limit)

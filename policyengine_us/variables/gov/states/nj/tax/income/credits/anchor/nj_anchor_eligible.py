from policyengine_us.model_api import *


class nj_anchor_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "New Jersey ANCHOR program eligibility"
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/treasury/taxation/anchor/",
        "https://www.nj.gov/treasury/taxation/anchor/calculated.shtml",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.credits.anchor

        # Get gross income at tax unit level
        gross_income = add(tax_unit, period, ["nj_gross_income"])

        # Determine if homeowner or renter based on property taxes and rent
        pays_property_taxes = add(tax_unit, period, ["real_estate_taxes"]) > 0
        pays_rent = tax_unit("rents", period)
        is_homeowner = pays_property_taxes & ~pays_rent
        is_renter = pays_rent & ~pays_property_taxes

        # Check income eligibility based on tenure type
        homeowner_income_eligible = is_homeowner & (
            gross_income <= p.homeowner.income_limit.upper
        )
        renter_income_eligible = is_renter & (
            gross_income <= p.renter.income_limit
        )

        return homeowner_income_eligible | renter_income_eligible

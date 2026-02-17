from policyengine_us.model_api import *


class nj_anchor(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey ANCHOR benefit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/treasury/taxation/anchor/",
        "https://www.nj.gov/treasury/taxation/anchor/calculated.shtml",
    )
    defined_for = "nj_anchor_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.credits.anchor

        # Get gross income
        gross_income = add(tax_unit, period, ["nj_gross_income"])

        # Determine if senior (age 65+ for head or spouse)
        greater_age = tax_unit("greater_age_head_spouse", period)
        is_senior = greater_age >= p.age_threshold

        # Determine if homeowner or renter
        pays_property_taxes = add(tax_unit, period, ["real_estate_taxes"]) > 0
        pays_rent = tax_unit("rents", period)
        is_homeowner = pays_property_taxes & ~pays_rent
        is_renter = pays_rent & ~pays_property_taxes

        # Determine income tier for homeowners
        lower_income = gross_income <= p.homeowner.income_limit.lower

        # Calculate homeowner benefit amounts
        homeowner_senior_amount = where(
            lower_income,
            p.homeowner.senior.amount.lower_income,
            p.homeowner.senior.amount.upper_income,
        )
        homeowner_non_senior_amount = where(
            lower_income,
            p.homeowner.non_senior.amount.lower_income,
            p.homeowner.non_senior.amount.upper_income,
        )
        homeowner_amount = where(
            is_senior, homeowner_senior_amount, homeowner_non_senior_amount
        )

        # Calculate renter benefit amounts
        renter_amount = where(
            is_senior, p.renter.senior.amount, p.renter.non_senior.amount
        )

        # Return benefit based on tenure type
        return where(
            is_homeowner, homeowner_amount, where(is_renter, renter_amount, 0)
        )

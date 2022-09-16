from openfisca_us.model_api import *


class mo_property_tax_credit_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO property tax credit demographic eligiblity test"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-PTS_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.025&bid=6438",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.030&bid=6439",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        return 0
        # short circuit until fully modeled
        # Currently not including railroad retirement or veterans benefits.
        rents = tax_unit("rents", period)
        cohabitates = tax_unit("lives_with_joint_filing_spouse", period)
        p = parameters(period).gov.states.mo.tax.income.credits.property_tax
        income_threshold = select(
            [
                rents & cohabitates,
                rents & ~cohabitates,
                ~rents & cohabitates,
                ~rents & ~cohabitates,
            ],
            [
                p.rent_cohabitating,
                p.rent_separate,
                p.own_cohabitating,
                p.own_separate,
            ],
        )

        # Determine if the tax unit head and spouse co-habitate

        rent = add(tax_unit, period, ["rent"])
        property_tax = add(tax_unit, period, ["real_estate_taxes"])

        total_household_income = add(
            tax_unit,
            period,
            [
                "mo_adjusted_gross_income",
                "pension_income",
                "mo_property_tax_credit_public_assistance",
            ],
        )

        meets_income_test = total_household_income <= income_threshold

        rent_expense_limit = p.rental_expense_cap
        rent_total = min_(rent, rent_expense_limit)

        property_tax_expense_limit = p.property_tax_expense_cap
        property_tax_total = min_(property_tax, property_tax_expense_limit)

        # Total credit basis comes from line 13 of MO-PTS, not in legislation, proscribes $1,100 cap just as property tax expense cap
        total_credit_basis = where(
            (rent_total + property_tax_total >= property_tax_expense_limit),
            property_tax_expense_limit,
            (rent_total + property_tax_total),
        )

        minimum_base = p.minimum_base

        # Check if rent/property tax > 1100
        # placehold to complete unit testing while waiting for comment from MO dept of revenue
        return total_credit_basis

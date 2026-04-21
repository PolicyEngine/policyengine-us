from policyengine_us.model_api import *


class mn_renters_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota renter's credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0693",
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1rent-25.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2025-12/m1ref-25.pdf",
    )
    defined_for = "mn_renters_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.renters
        household_income = tax_unit("mn_renters_credit_household_income", period)
        rent_constituting_property_taxes = tax_unit(
            "mn_rent_constituting_property_taxes", period
        )
        assistance_rent_paid = tax_unit(
            "mn_renters_credit_assistance_rent_paid", period
        )
        percent_of_income = p.percent_of_income.calc(household_income)
        claimant_share = p.claimant_share.calc(household_income)
        max_credit = p.max_credit.calc(household_income)

        excess_rent = max_(
            0, rent_constituting_property_taxes - percent_of_income * household_income
        )
        line_13_amount = round_(min_(max_credit, excess_rent * (1 - claimant_share)))
        # Per Minn. Stat. 290.0693, Subd. 6(b), the proration uses
        # adjusted gross income (M1RENT Line 5), not household income
        # (Line 10 after subtractions).
        agi = add(tax_unit, period, ["adjusted_gross_income"])
        proration_denominator = agi + assistance_rent_paid
        proration_ratio = where(
            proration_denominator > 0,
            round_(agi / proration_denominator, 5),
            0,
        )
        prorated_amount = where(
            assistance_rent_paid > 0,
            line_13_amount * proration_ratio,
            line_13_amount,
        )
        return round_(prorated_amount)

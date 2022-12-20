from policyengine_us.model_api import *


class mo_property_tax_credit_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO property tax credit amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-PTS_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.025&bid=6438",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.030&bid=6439",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):

        # OLD CODE
        rents = tax_unit("rents", period)
        cohabitates = tax_unit("lives_with_joint_filing_spouse", period)
        p = parameters(period).gov.states.mo.tax.income.credits.property_tax
        hh_income_threshold = select(
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
        # OLD CODE

        # determine gross household income
        gross_hh_income = add(
            tax_unit,
            period,
            [  # TODO: review all this
                "mo_adjusted_gross_income",
                "pension_income",  # TODO: fix
                "mo_property_tax_credit_public_assistance",  # TODO: fix
            ],
        )
        # determine household income offset
        # TODO: add code
        # determine net household income
        net_hh_income = gross_hh_income  # TODO: fix

        # compute credit basis
        rent = add(tax_unit, period, ["rent"])
        rent_fraction = 0.20  # TODO: make 0.20 be a parameter
        rent_expense_limit = p.rental_expense_cap
        rent_amount = min_(rent * rent_fraction, rent_expense_limit)
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        property_tax_expense_limit = p.property_tax_expense_cap
        property_tax_amount = min_(property_tax, property_tax_expense_limit)
        credit_basis = where(
            rent_amount + property_tax_amount >= property_tax_expense_limit,
            property_tax_expense_limit,
            rent_amount + property_tax_amount,
        )
        # compute credit amount using legislative formula (not form table)
        minimum_base = p.minimum_base
        phaseout_fraction = 0  # TODO: add calculation of fraction
        credit_amount = where(
            net_hh_income <= minimum_base,
            credit_basis,  # full credit
            where(
                net_hh_income > hh_income_threshold,
                0,  # no credit
                credit_basis * (1 - phaseout_fraction),
            ),
        )
        return credit_amount

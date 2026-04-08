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
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.renters
        household_income = tax_unit("mn_renters_credit_household_income", period)
        rent_constituting_property_taxes = tax_unit(
            "mn_rent_constituting_property_taxes", period
        )
        eligible = tax_unit("mn_renters_credit_eligible", period)

        percent_of_income = p.percent_of_income.calc(household_income)
        claimant_share = p.claimant_share.calc(household_income)
        max_credit = p.max_credit.calc(household_income)

        excess_rent = max_(
            0, rent_constituting_property_taxes - percent_of_income * household_income
        )
        credit_before_line_a = min_(max_credit, excess_rent * (1 - claimant_share))

        crp_line_a_amount = tax_unit("mn_renters_credit_crp_line_a_amount", period)
        total_household_basis = household_income + crp_line_a_amount
        mask = total_household_basis != 0
        ratio = np.divide(
            household_income,
            total_household_basis,
            out=np.zeros_like(total_household_basis),
            where=mask,
        )
        adjusted_credit = where(
            crp_line_a_amount > 0,
            credit_before_line_a * ratio,
            credit_before_line_a,
        )
        return eligible * adjusted_credit

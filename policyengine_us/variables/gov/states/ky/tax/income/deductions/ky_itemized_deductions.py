from policyengine_us.model_api import *


class ky_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "KY Itemized Deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.ky.gov/Forms/Form%20740%20Schedule%20A%202022.pdf"
        "https://law.justia.com/codes/kentucky/2022/chapter-141/section-141-019/"
    )
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        # Assume that married filing separate spouses each fill out their own Schedule A.
        # They are allowed to do this or file a joint Schedule A and divide by share of income.

        # Get home mortgage interest.
        home_mortgage_interest = tax_unit("home_mortgage_interest", period)

        # Get real estate/investment interest.
        investment_interest = tax_unit("investment_income_form_4952", period)

        # Get charitable contributions.
        # Assume that this includes artistic charitable contributions.
        cash_donations = add(tax_unit, period, ["charitable_cash_donations"])
        non_cash_donations = add(
            tax_unit, period, ["charitable_non_cash_donations"]
        )
        charitable_contributions = cash_donations + non_cash_donations

        # Get gambling losses, up to gambling winnings.
        gambling_losses = add(tax_unit, period, ["gambling_losses"])

        return (
            home_mortgage_interest
            + investment_interest
            + charitable_contributions
            + gambling_losses
        )

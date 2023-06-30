from policyengine_us.model_api import *


class nj_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey property tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-3a-20/"
    defined_for = "nj_property_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        # Get the NJ property tax credit portion of the parameter tree.
        p = parameters(period).gov.states.nj.tax.income.credits.property_tax

        # Check if the tax unit is taking the property tax deduction.
        taking_deduction = tax_unit("nj_taking_property_tax_deduction", period)

        # Return the credit amount, which does not depend on property taxes paid if eligible.
        # Halve the credit amount if filing separate but maintain same home.
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        separate = filing_status == status.SEPARATE
        cohabitating = tax_unit("cohabitating_spouses", period)
        credit_amount = p.amount / (1 + separate * cohabitating)

        return credit_amount * ~taking_deduction

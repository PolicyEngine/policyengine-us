from policyengine_us.model_api import *


class nj_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey property tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-3a-20/"
    defined_for = "nj_property_tax_deduction_or_credit_eligible"

    def formula(tax_unit, period, parameters):
        # Don't forget to add eligiblity (I think easy one is filing threshold).
        # Don't forget to divide the threshold if filing separately? They have to also live together.

        # Get the NJ property tax deduction portion of the parameter tree.
        p = parameters(
            period
        ).gov.states.nj.tax.income.property_tax_deduction_credit

        # Check that the tax unit is not taking the property tax deduction.
        not_taking_deduction = ~tax_unit(
            "nj_taking_property_tax_deduction", period
        )

        # Return the credit amount, which does not depend on property taxes paid if eligible.
        return p.credit_amount * not_taking_deduction

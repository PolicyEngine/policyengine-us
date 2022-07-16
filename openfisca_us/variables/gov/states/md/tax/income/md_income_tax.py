from openfisca_us.model_api import *


class md_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD income tax"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):

        before_credits = tax_unit("md_income_tax_before_credits", period)

        # This is out of order
        # But md_poverty_line_credit should make a call to md_non_refundable
        # which will then be subtracted
        # plc = tax_unit("md_poverty_line_credit", period),
        non_refundable_eitc = tax_unit("md_state_non_refundable_eitc", period)

        refundable_credits = tax_unit("md_refundable_credits", period)

        return (
            before_credits
            # - plc
            - non_refundable_eitc
        )

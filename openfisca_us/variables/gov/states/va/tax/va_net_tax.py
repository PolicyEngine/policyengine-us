from openfisca_us.model_api import *

class va_total_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Net taxes owed/refunded"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        tax_paid_to_other_states = 0  # TODO: fill this in
        va_sch_cr_credits = tax_unit("va_sch_cr_credits", period)
        total_credits = tax_paid_to_other_states + va_sch_cr_credits

        net_amount_of_tax = (
            tax_unit('va_tax_before_credits', period) -
            tax_unit('va_spouse_tax_adjustment', period)
        )

        # TODO: lines 20-33 on the 760. But most of those feel like they can be
        # ignored. They're about taxes withheld and voluntary contributions

        return net_amount_of_tax - total_credits
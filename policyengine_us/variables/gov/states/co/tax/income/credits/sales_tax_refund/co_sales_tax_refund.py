from policyengine_us.model_api import *


class co_sales_tax_refund(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado sales tax refund"
    unit = USD
    definition_period = YEAR
    reference = (
        # C.R.S. 39-22-2003(1)(a) defines a "qualified individual"; (2) allows
        # the refund only for a tax year whose fiscal year had excess state
        # revenues; (3) sets the per-person refund amount and its doubling for
        # a joint return.
        "https://leg.colorado.gov/sites/default/files/images/olls/crs2023-title-39.pdf",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=23",
    )
    defined_for = "co_sales_tax_refund_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.sales_tax_refund
        if p.amount.flat_amount_enabled:
            amount = p.amount.amount
        else:
            agi = tax_unit("co_modified_agi", period)
            amount = p.amount.scale.calc(agi)
        # The refund is claimed per qualifying individual (head and/or spouse),
        # so multiply the per-person amount by the number of eligible filers
        # rather than doubling for every joint return.
        eligible_count = add(tax_unit, period, ["co_sales_tax_refund_person_eligible"])
        return eligible_count * amount * p.in_effect

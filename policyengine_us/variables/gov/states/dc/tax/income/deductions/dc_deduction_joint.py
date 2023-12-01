from policyengine_us.model_api import *


class dc_deduction_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC deduction for each tax unit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        # DC individual income tax FAQs include this:
        # Q: If I claimed itemized deductions on my federal return, must I
        #    also itemize on my DC return?
        # A: Yes. If you claim itemized deductions on your federal tax return,
        #    you must itemize on your DC tax return. You must take the same
        #    type of deduction (itemized or standard) on your DC return as
        #    taken on your federal return.
        # https://otr.cfo.dc.gov/page/individual-income-tax-special-circumstances-faqs
        return where(
            tax_unit("tax_unit_itemizes", period),
            tax_unit("dc_itemized_deductions", period),
            tax_unit("dc_standard_deduction", period),
        )

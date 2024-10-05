from policyengine_us.model_api import *


class ks_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        # 2021 Form K-40 instructions say this:
        #   LINE 4 (Standard deduction or itemized deductions):
        #   If you did not itemize your deductions on your federal return,
        #   you may choose to itemize your deductions or claim the
        #   standard deduction on your Kansas return whichever is to your
        #   advantage.  If you itemized on your federal return, you may
        #   either itemize or take the standard deduction on your Kansas
        #   return, whichever is to your advantage.
        # compute itemized deduction maximum
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)
        uncapped_property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        return itm_deds_less_salt + uncapped_property_taxes

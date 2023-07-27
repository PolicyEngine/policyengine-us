from policyengine_us.model_api import *


class ne_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "NE itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdf"
        "https://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        # 2021 Form 1040N instructions say this:
        #   If you use the standard deduction on the federal return,
        #   you must use the Nebraska standard deduction on the
        #   Nebraska return.  All taxpayers that claimed itemized
        #   deductions on their federal return are allowed the larger
        #   of the Nebraska standard deduction or federal itemized
        #   deductions, minus state and local income taxes claimed on
        #   Federal Schedule A.
        us_itemizing = tax_unit("tax_unit_itemizes", period)
        # calculate US itemized deductions less state non-property taxes
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)
        capped_property_taxes = tax_unit("capped_property_taxes", period)
        ne_itm_deds = itm_deds_less_salt + capped_property_taxes
        return us_itemizing * ne_itm_deds

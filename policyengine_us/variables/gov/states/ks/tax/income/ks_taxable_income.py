from policyengine_us.model_api import *


class ks_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf",
        "https://www.ksrevenue.gov/pdf/ip22.pdf",
        "https://www.ksrevisor.gov/statutes/chapters/ch79/079_032_0120.html",
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.deductions.itemized
        std_ded = tax_unit("ks_standard_deduction", period)
        itm_ded = tax_unit("ks_itemized_deductions", period)
        # K.S.A. 79-32,120(a)(1): before 2021, only federal itemizers may
        # itemize on the Kansas return.
        may_itemize = True
        if p.federal_itemization_required:
            may_itemize = tax_unit("tax_unit_itemizes", period)
        deductions = where(may_itemize & (itm_ded > std_ded), itm_ded, std_ded)
        exemptions = tax_unit("ks_exemptions", period)
        return max_(0, tax_unit("ks_agi", period) - deductions - exemptions)

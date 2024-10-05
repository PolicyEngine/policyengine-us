from policyengine_us.model_api import *


class dc_income_tax_before_credits_joint(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC income tax before credits when married couples file jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=36"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=34"
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        taxinc = max_(0, tax_unit("dc_taxable_income_joint", period))
        p = parameters(period).gov.states
        return p.dc.tax.income.rates.calc(taxinc)

from policyengine_us.model_api import *


class dc_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC child and dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=36"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=34"
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        # DC matches the potential federal credit
        us_cdcc = tax_unit("cdcc_potential", period)
        p_dc = parameters(period).gov.states.dc.tax.income.credits
        return us_cdcc * p_dc.cdcc.match

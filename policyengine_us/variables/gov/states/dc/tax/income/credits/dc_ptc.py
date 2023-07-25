from policyengine_us.model_api import *


class dc_ptc(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=49"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=47"
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        rent = add(tax_unit, period, ["rent"])
        retax = add(tax_unit, period, ["real_estate_taxes"])
        p_dc = parameters(period).gov.states.dc.tax.income.credits
        ptax = retax + rent * p_dc.ptc.rent_ratio
        elderly_age = p_dc.ptc.min_elderly_age
        head_age = tax_unit("age_head", period)
        spouse_age = tax_unit("age_spouse", period)
        is_elderly = (head_age >= elderly_age) | (spouse_age >= elderly_age)
        us_agi = tax_unit("adjusted_gross_income", period)
        ptax_offset = us_agi * where(
            is_elderly,
            p_dc.ptc.fraction_elderly.calc(us_agi, right=True),
            p_dc.ptc.fraction_nonelderly.calc(us_agi, right=True),
        )
        uncapped_ptc = max_(0, ptax - ptax_offset)
        return min_(p_dc.ptc.max, uncapped_ptc)

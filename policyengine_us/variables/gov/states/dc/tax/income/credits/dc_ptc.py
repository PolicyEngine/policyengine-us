from policyengine_us.model_api import *


class dc_ptc(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=49",
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=47",
        # D.C. Code 47-1806.06(b)(4) (one claimant per tax filing unit) and (k)
        # (no credit for a claimant who was a dependent, unless 65 or older).
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.06",
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

        # Only positive AGI creates an offset (negative AGI should not reduce offset)
        us_agi = tax_unit("adjusted_gross_income", period)
        positive_agi = max_(0, us_agi)
        ptax_offset = positive_agi * where(
            is_elderly,
            p_dc.ptc.fraction_elderly.calc(positive_agi, right=True),
            p_dc.ptc.fraction_nonelderly.calc(positive_agi, right=True),
        )
        uncapped_ptc = max_(0, ptax - ptax_offset)
        # D.C. Code 47-1806.06(k): no credit for a claimant who was a dependent
        # under any income tax law that year, unless 65 or older; a couple can
        # claim it through a spouse who is not such a dependent ((b)(4)).
        has_claimant = tax_unit("dc_ptc_has_eligible_claimant", period)
        return (
            min_(p_dc.ptc.max, uncapped_ptc)
            * tax_unit("takes_up_dc_ptc", period)
            * has_claimant
        )

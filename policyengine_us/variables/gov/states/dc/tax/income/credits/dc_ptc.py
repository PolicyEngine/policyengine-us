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
        person = tax_unit.members
        rent = person("rent", period)
        retax = person("real_estate_taxes", period)
        p_dc = parameters(period).gov.states.dc.tax.income.credits
        ptax = retax + rent * p_dc.ptc.rent_ratio

        elderly_age = p_dc.ptc.min_elderly_age
        age = person("age", period)
        is_elderly = age >= elderly_age

        # Only positive AGI creates an offset (negative AGI should not reduce offset)
        us_agi = tax_unit("adjusted_gross_income", period)
        positive_agi = tax_unit.project(max_(0, us_agi))
        ptax_offset = positive_agi * where(
            is_elderly,
            p_dc.ptc.fraction_elderly.calc(positive_agi, right=True),
            p_dc.ptc.fraction_nonelderly.calc(positive_agi, right=True),
        )
        uncapped_ptc = max_(0, ptax - ptax_offset)
        # Sections (b)(4) and (b)(8) allow one claimant's own payments.
        # Each eligible spouse can claim using their own age and payments.
        filer = person("is_tax_unit_head_or_spouse", period)
        dependent = person("claimable_as_dependent_on_another_return", period)
        eligible_claimant = filer & (
            ~dependent | (age >= p_dc.ptc.dependent_claimant_min_age)
        )
        claimant_ptc = where(eligible_claimant, uncapped_ptc, 0)
        return min_(p_dc.ptc.max, tax_unit.max(claimant_ptc)) * tax_unit(
            "takes_up_dc_ptc", period
        )

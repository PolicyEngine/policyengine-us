from policyengine_us.model_api import *


class ia_liheap_fixed_income_only(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Iowa LIHEAP household has fixed income only"
    documentation = (
        "Whether every dollar of the household's countable income before the "
        "child support deduction comes from Social Security, SSI, veterans' "
        "benefits or pensions. Definitions, Fixed Income Household: 'Only mark "
        '"fixed income" when that is the ONLY source(s) of income.\' A '
        "household with no countable income is not fixed income only."
    )
    reference = (
        # Definitions, Fixed Income Household (page 81); Appendix I, Fixed
        # Income Only (no other sources of income) (page 137); Appendix C notes
        # that alimony, variable annuities and child support are not fixed
        # income (pages 90-92).
        "https://hhs.iowa.gov/media/17262/download?inline#page=81",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.liheap.income
        gross = add(
            spm_unit,
            period,
            [
                "ia_liheap_countable_earned_income",
                "ia_liheap_countable_unearned_income",
            ],
        )
        person = spm_unit.members
        adult = person("age", period) >= p.countable_min_age
        # sources/fixed.yaml lists the fixed sources in the same relative order
        # as sources/unearned.yaml, so the two sums are bit-identical when every
        # other source is zero.
        fixed = spm_unit.sum(where(adult, add(person, period, p.sources.fixed), 0))
        return (gross > 0) & (fixed == gross)

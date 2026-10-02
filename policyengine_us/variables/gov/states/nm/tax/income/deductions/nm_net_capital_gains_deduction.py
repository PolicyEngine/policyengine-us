from policyengine_us.model_api import *


class nm_net_capital_gains_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico net capital gain deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503882/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgAcwgEwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA",
        # 2019 HB6, section 14: NMSA 7-2-34(B) gives each spouse filing
        # separately one-half of the joint-return deduction, and 7-2-34(D)
        # adopts IRC 1222(11).
        "https://www.nmlegis.gov/Sessions/19%20Regular/final/HB0006.pdf#page=41",
        # 2019 HB6, section 59(A): section 14 applies from tax year 2019.
        "https://www.nmlegis.gov/Sessions/19%20Regular/final/HB0006.pdf#page=105",
        # 2024 HB252, section 8: from 2025 (section 42(B)) subsection (B) keeps
        # the separate-return rule and the same definition is in NMSA
        # 7-2-34(C).
        "https://www.nmlegis.gov/Sessions/24%20Regular/final/HB0252.pdf#page=30",
        # 2023 PIT-ADJ instructions, line 16.
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/90560f4e-0ef0-4e52-a003-878b84f858bb/PITbook2023.pdf#page=53",
        "https://www.law.cornell.edu/uscode/text/26/1222#11",
        # Capital gain distributions are long-term capital gains.
        "https://www.law.cornell.edu/uscode/text/26/852#b_3_B",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.tax.income.deductions.net_capital_gains
        # Capital gain distributions reported without Schedule D are
        # long-term capital gains under IRC 852(b)(3)(B).
        unit_long_term_gain = add(
            tax_unit, period, ["long_term_capital_gains", "non_sch_d_capital_gains"]
        )
        unit_short_term_gain = add(tax_unit, period, ["short_term_capital_gains"])
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        # NMSA 7-2-34(B) (2019 HB6, section 14(B); 2024 HB252, section 8(B))
        # gives each spouse filing separately one-half of the deduction that
        # would have been allowed on the joint return, so the deduction is
        # computed on the couple's combined gains and losses. Each spouse
        # filing separately heads their own tax unit; reach the other spouse's
        # unit through the marital unit only when it holds exactly two people
        # who both head a separate-filing unit: without explicit marital
        # units, everyone shares one default unit.
        person = tax_unit.members
        separate_head = person("is_tax_unit_head", period) & tax_unit.project(separate)
        couple = (person.marital_unit.nb_persons() == 2) & (
            person.marital_unit.sum(separate_head) == 2
        )
        # Only the head of a separate-filing unit can be in such a couple, so
        # each tax unit sums at most one couple member's combined amount.
        pooled = tax_unit.any(couple)
        couple_long_term_gain = tax_unit.sum(
            couple * person.marital_unit.sum(tax_unit.project(unit_long_term_gain))
        )
        couple_short_term_gain = tax_unit.sum(
            couple * person.marital_unit.sum(tax_unit.project(unit_short_term_gain))
        )
        long_term_gain = where(pooled, couple_long_term_gain, unit_long_term_gain)
        short_term_gain = where(pooled, couple_short_term_gain, unit_short_term_gain)
        # NMSA 7-2-34 defines "net capital gain" by IRC Section 1222(11): net
        # long-term capital gain less any net short-term capital loss, so
        # short-term gains are excluded. The definition is in subsection (D)
        # for 2019 through 2024 (2019 HB6, sections 14 and 59(A)) and in
        # subsection (C) from 2025 (2024 HB252, sections 8 and 42(B)).
        net_short_term_loss = max_(0, -short_term_gain)
        net_capital_gains = max_(0, long_term_gain - net_short_term_loss)
        uncapped_element = p.uncapped_element_percent * net_capital_gains
        capped_element = p.capped_element.calc(net_capital_gains)
        joint_return_deduction = max_(uncapped_element, capped_element)
        share = where(separate, p.separate_filer_share, 1)
        return share * joint_return_deduction

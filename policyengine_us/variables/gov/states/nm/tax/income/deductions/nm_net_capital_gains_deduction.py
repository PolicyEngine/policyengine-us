from policyengine_us.model_api import *


class nm_net_capital_gains_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico net capital gain deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503882/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgAcwgEwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA",
        # 2019 HB6, section 14: NMSA 7-2-34(D) adopts IRC 1222(11).
        "https://www.nmlegis.gov/Sessions/19%20Regular/final/HB0006.pdf#page=41",
        # 2019 HB6, section 59(A): section 14 applies from tax year 2019.
        "https://www.nmlegis.gov/Sessions/19%20Regular/final/HB0006.pdf#page=105",
        # 2024 HB252, section 8: from 2025 (section 42(B)) the same definition
        # is in NMSA 7-2-34(C).
        "https://www.nmlegis.gov/Sessions/24%20Regular/final/HB0252.pdf#page=30",
        "https://www.law.cornell.edu/uscode/text/26/1222#11",
        # Capital gain distributions are long-term capital gains.
        "https://www.law.cornell.edu/uscode/text/26/852#b_3_B",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.tax.income.deductions.net_capital_gains
        # Capital gain distributions reported without Schedule D are
        # long-term capital gains under IRC 852(b)(3)(B).
        long_term_gain = add(
            tax_unit, period, ["long_term_capital_gains", "non_sch_d_capital_gains"]
        )
        short_term_gain = add(tax_unit, period, ["short_term_capital_gains"])
        # NMSA 7-2-34 defines "net capital gain" by IRC Section 1222(11): net
        # long-term capital gain less any net short-term capital loss, so
        # short-term gains are excluded. The definition is in subsection (D)
        # for 2019 through 2024 (2019 HB6, sections 14 and 59(A)) and in
        # subsection (C) from 2025 (2024 HB252, sections 8 and 42(B)).
        net_short_term_loss = max_(0, -short_term_gain)
        net_capital_gains = max_(0, long_term_gain - net_short_term_loss)
        uncapped_element = p.uncapped_element_percent * net_capital_gains
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        # Halve the deduction if filing separately. Limitation: the law
        # (2019 HB6, section 14(B)) halves the deduction allowed on the joint
        # return, which requires the couple's combined gains; each separate
        # unit here uses only its own gains.
        denominator = where(separate, 2, 1)
        capped_element = p.capped_element.calc(net_capital_gains)
        numerator = max_(uncapped_element, capped_element)
        return numerator / denominator

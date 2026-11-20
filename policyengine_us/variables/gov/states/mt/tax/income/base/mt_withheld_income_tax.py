from policyengine_us.model_api import *

# Montana's rate schedules for each filing status, by parameter node name.
FILING_STATUS_NODES = {
    "SINGLE": "single",
    "JOINT": "joint",
    "HEAD_OF_HOUSEHOLD": "head_of_household",
    "SEPARATE": "separate",
    "SURVIVING_SPOUSE": "surviving_spouse",
}


def by_filing_status(filing_status, value_for_node):
    status = filing_status.possible_values
    return select(
        [filing_status == status[name] for name in FILING_STATUS_NODES],
        [value_for_node(node) for node in FILING_STATUS_NODES.values()],
    )


class mt_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Montana withheld income tax"
    documentation = (
        "Estimate of Montana income tax for the federal SALT deduction. It "
        "reads AGI, filing status and capital gains, not the deduction "
        "choice, so federal itemization does not depend on itself."
    )
    defined_for = StateCode.MT
    unit = USD
    definition_period = YEAR
    reference = (
        # MCA 15-30-2103: rates by filing status from 2024, with net
        # long-term capital gains taxed at separate rates.
        "https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0030/0150-0300-0210-0030.html",
        # Form 2 starts from federal taxable income from 2024.
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=8",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income
        agi = person("adjusted_gross_income_person", period)
        if p.married_filing_separately_on_same_return_allowed:
            # Before 2024 one rate schedule applied to every filing status
            # and spouses could file separately on the same return, so each
            # person's tax is estimated from their own AGI.
            standard_deduction = p.deductions.standard.cap["SINGLE"]
            return p.main.single.calc(max_(agi - standard_deduction, 0))

        # From 2024 Montana starts from federal taxable income and sets its
        # brackets by filing status. Estimate the tax unit's tax on its AGI
        # less the federal basic standard deduction for its filing status,
        # then give each person their share of the unit's positive AGI.
        # person.tax_unit returns each person's tax unit value.
        tax_unit = person.tax_unit
        filing_status = tax_unit("filing_status", period)
        standard_deduction = parameters(period).gov.irs.deductions.standard.amount[
            filing_status
        ]
        unit_agi = tax_unit.sum(agi)
        taxable_income = max_(unit_agi - standard_deduction, 0)

        capital_gains = 0
        capital_gains_tax = 0
        cg = p.main.capital_gains
        if cg.in_effect:
            # Form 2 line 2: net long-term capital gain, limited by any
            # short-term capital loss.
            ltcg = tax_unit.sum(person("long_term_capital_gains", period))
            stcg = tax_unit.sum(person("short_term_capital_gains", period))
            capital_gains = min_(max_(min_(ltcg, ltcg + stcg), 0), taxable_income)
            ordinary_income = taxable_income - capital_gains
            threshold = by_filing_status(
                filing_status, lambda node: cg.rates[node].thresholds[-1]
            )
            lower_rate = by_filing_status(
                filing_status, lambda node: cg.rates[node].amounts[0]
            )
            higher_rate = by_filing_status(
                filing_status, lambda node: cg.rates[node].amounts[-1]
            )
            gains_below_threshold = min_(
                max_(threshold - ordinary_income, 0), capital_gains
            )
            capital_gains_tax = (
                gains_below_threshold * lower_rate
                + (capital_gains - gains_below_threshold) * higher_rate
            )

        ordinary_tax = by_filing_status(
            filing_status,
            lambda node: p.main[node].calc(taxable_income - capital_gains),
        )
        unit_tax = ordinary_tax + capital_gains_tax

        positive_agi = max_(agi, 0)
        unit_positive_agi = tax_unit.sum(positive_agi)
        share = np.divide(
            positive_agi,
            unit_positive_agi,
            out=np.zeros_like(positive_agi),
            where=unit_positive_agi > 0,
        )
        return unit_tax * share

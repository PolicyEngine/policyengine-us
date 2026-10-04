from policyengine_us.model_api import *


class ia_liheap_countable_unearned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Iowa LIHEAP countable unearned income"
    documentation = (
        "Unearned income of household members aged 18 and over counted under "
        "Appendix C: Social Security, SSI, pensions and retirement "
        "distributions, railroad retirement, unemployment and workers' "
        "compensation, strike benefits, disability and veterans' benefits, "
        "alimony, rental income, interest, dividends and gambling winnings. "
        "Approximations: Social Security is counted gross; Iowa counts the "
        "amount paid net of Medicare premiums and SSA repayments, and netting "
        "the Medicare Part B premium is deferred under coordinator ruling D6 "
        "while SSA repayments have no input. All interest is counted although "
        "Iowa excludes interest on bank accounts; dividends are counted in full "
        "although Iowa ignores a combined annual total under $120. Social "
        "Security paid to members under 18 is recorded at $0.00 and is "
        "excluded here with all other under-18 income."
    )
    reference = (
        # Section 6.10 (page 25), Section 6.20 (page 26) and Appendix C rows
        # for Alimony (page 90), Disability Insurance (page 94), Dividends
        # (page 96), Gambling (page 99), Interest (page 103), IRA (page 103),
        # Pensions (page 109), Railroad Retirement (page 110), Rental Income
        # (page 110), Retirement (page 111), Social Security Benefits (page
        # 114), Strike Benefits (page 115), Unemployment (page 117), Veterans
        # Benefits (pages 118-119) and Workers Compensation (page 121).
        "https://hhs.iowa.gov/media/17262/download?inline#page=114",
        # Section 1.9, page 6.
        "https://liheapch.acf.gov/docs/2026/state-plans/IA_Plan_2026.pdf#page=6",
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.hhs.liheap.income
        # ssi is a monthly variable; add() sums the twelve months.
        unearned = add(person, period, p.sources.unearned)
        age = person("age", period)
        # Appendix C, Social Security Benefits: "Only count for HH members 18
        # and older"; payments to members under 18 are recorded at $0.00.
        return where(age >= p.countable_min_age, unearned, 0)

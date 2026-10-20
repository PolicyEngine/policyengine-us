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
        "amount paid net of Medicare premiums and SSA repayments, netting the "
        "Medicare Part B premium is deferred, as in Kansas, and SSA repayments "
        "have no input. All interest is counted although "
        "Iowa excludes interest on bank accounts; dividends are counted in full "
        "although Iowa ignores a combined annual total under $120. Social "
        "Security paid to members under 18 is recorded at $0.00 and is "
        "excluded here with all other under-18 income."
    )
    reference = (
        # Sections 6.10 and 6.20 and Appendix C rows for Alimony, Disability
        # Insurance, Dividends, Gambling, Interest, IRA, Pensions, Railroad
        # Retirement, Rental Income, Retirement, Social Security Benefits,
        # Strike Benefits, Unemployment, Veterans Benefits and Workers
        # Compensation.
        # PDF pages 25-26, 90, 94-96, 99, 103, 109-111, 114-115, 117-119, 121
        "https://hhs.iowa.gov/media/17262/download?inline#page=25",
        # Section 1.9.
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

from policyengine_us.model_api import *


class ia_liheap_countable_unearned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Iowa LIHEAP countable unearned income"
    documentation = (
        "Unearned income of household members aged 18 and over counted under "
        "Appendix C: Social Security, SSI, Iowa State Supplementary "
        "Assistance, pensions and retirement "
        "distributions, railroad retirement, unemployment and workers' "
        "compensation, strike benefits, disability and veterans' benefits, "
        "alimony, rental income, interest, dividends and gambling winnings. "
        "Each source is floored at zero, so a loss in one source (such as a "
        "rental loss) does not offset other income. Social Security is counted "
        "net of the out-of-pocket Medicare Part B premium; SSA repayments and "
        "Part D premiums have no input. No Part A premium is subtracted, "
        "because a Social Security beneficiary aged 65 or older is entitled to "
        "Part A without one under 42 U.S.C. 426(a), so none is withheld from "
        "the check. Approximations: all interest is counted "
        "although Iowa excludes interest on bank accounts; dividends are "
        "counted in full although Iowa ignores a combined annual total under "
        "$120. Social Security paid to members under 18 is recorded at $0.00 "
        "and is excluded here with all other under-18 income."
    )
    reference = (
        # Sections 6.10 and 6.20 and Appendix C rows for Alimony, Disability
        # Insurance, Dividends, Gambling, Interest, IRA, Pensions, Railroad
        # Retirement, Rental Income, Retirement, Social Security Benefits,
        # Strike Benefits, Unemployment, Veterans Benefits and Workers
        # Compensation.
        # PDF pages 25-26, 90, 94-96, 99, 103, 109-111, 114-115, 117-119, 121
        "https://hhs.iowa.gov/media/17262/download?inline#page=25",
        # Sections 1.8-1.9.
        # PDF pages 5-6
        "https://liheapch.acf.gov/docs/2026/state-plans/IA_Plan_2026.pdf#page=5",
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.hhs.liheap.income
        # Plan Section 1.8 (page 5) and Section 6.20 (page 26) count gross
        # income, and Appendix C Rental Income (page 110) counts "Income
        # received from rental properties". Each source is floored at zero, so
        # a loss in one source cannot offset another.
        unearned = 0
        for source in p.sources.unearned:
            # ADD sums monthly sources such as ssi over the year.
            unearned = unearned + max_(person(source, period, options=[ADD]), 0)
        # Plan Section 1.9 (page 6) counts Social Security Administration
        # benefits "Excluding MediCare deduction". Section 6.10 (page 25) and
        # Appendix C, Social Security Benefits (page 114), count "the net
        # amount" and use the amount "paid by check or direct deposit" as shown
        # on the SSA-1099. medicare_part_b_premium is zero for a person who is
        # not enrolled and excludes the share a Medicare Savings Program pays,
        # which is not withheld from the check. Only Part B comes off: under
        # 42 U.S.C. 426(a) a Social Security beneficiary aged 65 or older is
        # entitled to Part A, so no Part A premium is withheld.
        premium = person("medicare_part_b_premium", period)
        social_security = max_(person("social_security", period) - premium, 0)
        age = person("age", period)
        # Appendix C, Social Security Benefits: "Only count for HH members 18
        # and older"; payments to members under 18 are recorded at $0.00.
        return where(age >= p.countable_min_age, unearned + social_security, 0)

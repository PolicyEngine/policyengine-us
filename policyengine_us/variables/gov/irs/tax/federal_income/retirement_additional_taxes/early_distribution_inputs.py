"""Inputs for the additional tax on early distributions (Form 5329 Part I).

Amounts are the taxable parts of distributions already reported in the
person's retirement income inputs (for example taxable_ira_distributions or
taxable_pension_income); they are memo lines and add no income. The
simulator decides which exception a distribution meets; PolicyEngine applies
the statutory dollar caps.
"""

from policyengine_us.model_api import *

_REF = (
    "https://www.law.cornell.edu/uscode/text/26/72#t",
    "https://www.irs.gov/instructions/i5329",
)


def _money(name, label, documentation, reference=_REF):
    globals()[name] = type(
        name,
        (Variable,),
        dict(
            value_type=float,
            entity=Person,
            definition_period=YEAR,
            unit=USD,
            label=label,
            documentation=documentation,
            reference=reference,
            __module__=__name__,
        ),
    )


def _count(name, label, documentation):
    globals()[name] = type(
        name,
        (Variable,),
        dict(
            value_type=int,
            entity=Person,
            definition_period=YEAR,
            label=label,
            documentation=documentation,
            reference=_REF,
            __module__=__name__,
        ),
    )


_money(
    "early_distributions_from_retirement_plans",
    "Early distributions from qualified plans and IRAs",
    "Taxable distributions received before age 59 1/2 from qualified plans, "
    "403(b) and governmental 457(b) plans and IRAs (Form 5329 line 1), "
    "excluding SIMPLE IRA distributions in the first two years of "
    "participation and rollovers.",
)
_money(
    "early_distributions_from_simple_ira_first_two_years",
    "Early SIMPLE IRA distributions in the first two years of participation",
    "Taxable early distributions from a SIMPLE IRA received within two years "
    "of first participation (IRC 72(t)(6)).",
)
_money(
    "early_distributions_from_annuity_contracts",
    "Premature distributions from annuity contracts",
    "Taxable distributions received before age 59 1/2 from annuity contracts "
    "outside qualified plans (IRC 72(q)).",
    ("https://www.law.cornell.edu/uscode/text/26/72#q",),
)
_money(
    "early_distribution_exceptions_uncapped",
    "Early distributions excepted under uncapped exceptions",
    "Part of early_distributions_from_retirement_plans that meets an "
    "exception with no dollar cap: death, disability, terminal illness, "
    "substantially equal periodic payments, separation from service in or "
    "after the year of age 55 (plans only), QDRO, IRS levy, reservist, "
    "health insurance while unemployed or higher education (IRAs only), "
    "corrective distributions and similar.",
)
_money(
    "early_distribution_exceptions_simple_ira",
    "SIMPLE IRA two-year early distributions excepted",
    "Part of early_distributions_from_simple_ira_first_two_years that meets "
    "any IRC 72(t)(2) exception.",
)
_money(
    "early_distribution_exceptions_annuity",
    "Annuity premature distributions excepted",
    "Part of early_distributions_from_annuity_contracts that meets an IRC "
    "72(q)(2) exception: death, disability, substantially equal periodic "
    "payments, immediate annuities, investment before August 14, 1982 and "
    "similar.",
    ("https://www.law.cornell.edu/uscode/text/26/72#q_2",),
)
_money(
    "early_distribution_first_time_homebuyer",
    "IRA early distributions for a first-time home purchase",
    "IRA distributions used for qualified first-time homebuyer expenses (IRC "
    "72(t)(2)(F)). Capped at the lifetime limit less prior use.",
)
_money(
    "early_distribution_first_time_homebuyer_prior_use",
    "First-time homebuyer exception used in earlier years",
    "Amount of the lifetime first-time homebuyer exception claimed in prior years.",
)
_money(
    "early_distribution_birth_or_adoption",
    "Qualified birth or adoption distributions",
    "Distributions within one year of a birth or adoption (IRC 72(t)(2)(H)).",
)
_count(
    "early_distribution_birth_or_adoption_children",
    "Children born or adopted for the birth or adoption exception",
    "Number of children whose birth or adoption the distributions relate to; "
    "each child carries its own cap.",
)
_money(
    "early_distribution_emergency_personal_expense",
    "Emergency personal expense distributions",
    "Emergency personal expense distributions (IRC 72(t)(2)(I)); one per year, capped.",
)
_money(
    "early_distribution_domestic_abuse_victim",
    "Distributions to a domestic abuse victim",
    "Eligible distributions to a domestic abuse victim (IRC 72(t)(2)(K)). "
    "The simulator should also limit them to 50% of the vested balance.",
)
_money(
    "early_distribution_qualified_disaster",
    "Qualified disaster recovery distributions",
    "Qualified disaster recovery distributions (IRC 72(t)(2)(M)).",
)
_count(
    "early_distribution_qualified_disasters",
    "Qualified disasters for the disaster exception",
    "Number of federally declared disasters the distributions relate to; "
    "each disaster carries its own cap.",
)
_money(
    "early_distribution_medical_expense",
    "Early distributions claimed under the medical expense exception",
    "Early distributions claimed against unreimbursed medical expenses above "
    "the AGI floor (IRC 72(t)(2)(B)). Capped at the tax unit's medical "
    "expenses above the floor.",
)

"""Inputs for required minimum distributions and the excise tax on missed
distributions (IRC 401(a)(9), 408(a)(6), 4974; Form 5329 Part IX)."""

from policyengine_us.model_api import *

_REF = (
    "https://www.law.cornell.edu/uscode/text/26/401#a_9",
    "https://www.law.cornell.edu/uscode/text/26/4974",
    "https://www.irs.gov/publications/p590b",
)


def _input(name, value_type, label, documentation, unit=None):
    attributes = dict(
        value_type=value_type,
        entity=Person,
        definition_period=YEAR,
        label=label,
        documentation=documentation,
        reference=_REF,
        __module__=__name__,
    )
    if unit:
        attributes["unit"] = unit
    globals()[name] = type(name, (Variable,), attributes)


_input(
    "rmd_ira_prior_year_end_balance",
    float,
    "Traditional, SEP and SIMPLE IRA balance at the end of the prior year",
    "Aggregate December 31 balance of the person's own traditional, SEP and "
    "SIMPLE IRAs (not Roth or inherited IRAs). IRAs may be aggregated.",
    USD,
)
_input(
    "rmd_ira_distributions_taken",
    float,
    "IRA distributions counted toward the IRA required minimum distribution",
    "Distributions from the person's own traditional, SEP and SIMPLE IRAs in "
    "the year, excluding rollovers and corrective distributions.",
    USD,
)
_input(
    "rmd_employer_plan_prior_year_end_balance",
    float,
    "Employer plan balance at the end of the prior year",
    "December 31 balance of the person's own 401(a), 401(k), 403(b) and "
    "governmental 457(b) accounts. Use one plan, or plans whose required "
    "distributions may be aggregated (403(b)s); plans that cannot be "
    "aggregated need their shortfalls computed separately.",
    USD,
)
_input(
    "rmd_employer_plan_distributions_taken",
    float,
    "Employer plan distributions counted toward the plan required minimum distribution",
    "Distributions from the employer plans in rmd_employer_plan_prior_year_end_balance.",
    USD,
)
_input(
    "rmd_employer_plan_still_working",
    bool,
    "Still working for the plan sponsor (and not a 5% owner)",
    "Defers employer plan required distributions until retirement (IRC 401(a)(9)(C)(i)(II)).",
)
_input(
    "rmd_qlac_value_ira",
    float,
    "Value of qualifying longevity annuity contracts held in IRAs",
    "December 31 value of QLACs included in the IRA balance; excluded from "
    "the required distribution base if premiums are within the limit.",
    USD,
)
_input(
    "rmd_qlac_value_employer_plan",
    float,
    "Value of qualifying longevity annuity contracts held in employer plans",
    "December 31 value of QLACs included in the employer plan balance.",
    USD,
)
_input(
    "rmd_qlac_premiums_paid",
    float,
    "Total premiums paid for qualifying longevity annuity contracts",
    "Cumulative QLAC premiums across all plans and IRAs. Above the limit, "
    "the contracts are not QLACs and stay in the balance.",
    USD,
)
_input(
    "rmd_first_year_deferred",
    bool,
    "First required distribution deferred to April 1 of next year",
    "The current year is the first distribution year and the person will "
    "take its required distribution by April 1 of next year.",
)
_input(
    "rmd_prior_year_deferred_amount",
    float,
    "Required distribution for the prior year deferred to April 1 of this year",
    "First-year required distribution from last year that is due by April 1 "
    "of this year.",
    USD,
)
_input(
    "rmd_distribution_period_override",
    float,
    "Distribution period overriding the Uniform Lifetime Table",
    "For a sole spouse beneficiary more than 10 years younger, the Joint and "
    "Last Survivor Table period. 0 uses the Uniform Lifetime Table.",
)
_input(
    "rmd_inherited_required_amount",
    float,
    "Required distributions from inherited accounts",
    "Beneficiary required distributions from inherited IRAs and plans, as "
    "computed by the simulator (Single Life Table or 10-year rule).",
    USD,
)
_input(
    "rmd_inherited_distributions_taken",
    float,
    "Distributions taken from inherited accounts",
    "Distributions from inherited IRAs and plans in the year.",
    USD,
)
_input(
    "rmd_shortfall_corrected_timely",
    bool,
    "Missed required distribution corrected within the correction window",
    "The shortfall was distributed within the IRC 4974(e) correction window, "
    "so the reduced rate applies.",
)
_input(
    "rmd_excise_waiver_amount",
    float,
    "Shortfall for which the excise tax waiver is requested",
    "Part of the shortfall due to reasonable error that is being remedied "
    "(IRC 4974(d)).",
    USD,
)

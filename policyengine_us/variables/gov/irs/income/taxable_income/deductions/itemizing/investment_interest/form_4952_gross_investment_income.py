from policyengine_us.model_api import *


class form_4952_gross_investment_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Form 4952 gross investment income"
    unit = USD
    definition_period = YEAR
    documentation = """
    Form 4952 line 4a: "Gross income from property held for investment
    (excluding any net gain from the disposition of property held for
    investment)". Sum taxable interest and ordinary dividends (including
    qualified dividends) of nondependent tax-unit members, matching the
    is_tax_unit_dependent exclusion in irs_gross_income and AGI. Dependents'
    own interest and dividends are not attributed to the filer's return.
    Ordinary dividends contain only qualified and non-qualified dividends;
    the separately modeled Alaska Permanent Fund dividend is excluded, as
    the line 4a instructions require.

    Line 4a omits non-employer annuities because the pension inputs do not
    separate them from employer pensions, and royalties because they are
    not separated from rental_income. Schedule K-1 portfolio items, net
    investment income from estates and trusts, Form 8814 child income,
    and publicly traded partnership passive income have no separate inputs
    identifying the amounts that belong on this line. Employer pensions
    are compensation under 26 CFR 1.469-2T(c)(4)(i)(C)-(D), including
    "deferred compensation for services". On that basis, the model treats
    them as compensation rather than income from property held for investment.
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_4_B_i",
        "https://www.law.cornell.edu/uscode/text/26/163#d_5",
        "https://www.law.cornell.edu/cfr/text/26/1.469-2T",
        "https://www.irs.gov/pub/irs-prior/f4952--2025.pdf#page=3",
    ]

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_add(
            tax_unit, period, ["taxable_interest_income", "ordinary_dividend_income"]
        )

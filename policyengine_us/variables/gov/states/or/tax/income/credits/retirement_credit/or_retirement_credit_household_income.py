from policyengine_us.model_api import *


class or_retirement_credit_household_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Household income for the Oregon Retirement Income Tax Credit"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Household income under ORS 316.157(2)(b) and (c): the federal "
        "adjusted gross income of the taxpayer and spouse without their "
        "Social Security benefits, plus the otherwise exempt income listed in "
        "(2)(c)(A) and the net losses above $1,000 per category that "
        "(2)(c)(B) disallows."
    )
    reference = (
        # ORS 316.157(2)(b), (c) and (f), 2023 edition, PDF pages 25-26.
        "https://www.oregonlegislature.gov/bills_laws/Archive/2023ors316.pdf#page=25",
        # ORS 316.157, 2025 edition.
        "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2025.pdf#page=107",
        "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2025.pdf#page=127",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        p = (
            parameters(period)
            .gov.states["or"]
            .tax.income.credits.retirement_income.household_income
        )
        # ORS 316.157(2)(c): "Income" means federal adjusted gross income,
        # with the modifications below.
        agi = tax_unit("adjusted_gross_income", period)
        # (2)(b): household income "does not include Social Security benefits
        # received by the taxpayer or the spouse", which (2)(f) defines as
        # IRC 86 benefits.
        taxable_social_security = add(tax_unit, period, ["taxable_social_security"])
        # (2)(c)(A): otherwise exempt income. (2)(b) counts the income of the
        # taxpayer and spouse, so a dependent's own amounts are left out,
        # except amounts the taxpayer receives that may be recorded on a
        # child, such as child support.
        exempt_income = tax_unit_non_dep_add(
            tax_unit,
            period,
            p.additions,
            include_dependents=p.filer_amounts_recorded_on_dependents,
        )
        # (2)(c)(B)(i)-(iv): net losses above the limit in each category.
        disallowed_losses = tax_unit("or_retirement_credit_disallowed_losses", period)
        return agi - taxable_social_security + exempt_income + disallowed_losses

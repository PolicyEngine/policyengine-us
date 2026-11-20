from policyengine_us.model_api import *


class or_retirement_credit_disallowed_losses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Disallowed losses in household income for the Oregon Retirement Income Tax Credit"
    unit = USD
    definition_period = YEAR
    documentation = (
        "The losses that ORS 316.157(2)(c)(B)(i) to (iv) add back to federal "
        "adjusted gross income in computing household income: in each of four "
        "categories (property dispositions, farms, trades or businesses, and "
        "rents and royalties), the taxpayer's and spouse's net loss as "
        "deducted in adjusted gross income, to the extent it exceeds $1,000."
    )
    reference = (
        # ORS 316.157(2)(c)(B), 2023 edition, PDF pages 25-26.
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
        # ORS 316.157(2)(c)(B): "Adjusted gross income shall be increased due
        # to the disallowance of" the "net loss, in excess of $1,000" in each
        # category. Publication OR-17 (page 107): "Combine all income from
        # similar sources for net income or loss. Any net loss from the source
        # is limited to $1,000." Each category nets the head's and spouse's
        # income and losses as adjusted gross income includes them; the
        # model does not split a category's income by activity.
        categories = (
            # (B)(i) "all dispositions of tangible or intangible properties":
            # the capital gain or loss on Form 1040 line 7a, where a net loss
            # is limited under IRC 1211(b), and Form 4797 gains and losses.
            # A capital loss carryover used in the year is already netted in
            # line 7a (IRC 1212(b)). The statute disallows net operating loss
            # carryovers ((B)(v)) but no capital loss carryover, so it is not
            # added back, though Publication OR-17 (pages 107 and 127) does
            # not allow capital loss carryforwards.
            ["filer_loss_limited_net_capital_gains", "other_net_gain"],
            # (B)(ii) "the operation of a farm or farms": Schedule F.
            ["farm_operations_income"],
            # (B)(iii) "all operations of a trade or business, profession or
            # other activity entered into for the production or collection of
            # income": Schedule C, and partnership and S corporation income.
            ["total_self_employment_income", "partnership_s_corp_income"],
            # (B)(iv) "tangible or intangible property held for the production
            # of rents, royalties or other income": Schedule E rents and
            # royalties, Form 4835 farm rents, and estate and trust income.
            ["rental_income", "farm_rent_income", "estate_income"],
        )
        disallowed_losses = 0
        for sources in categories:
            net_income = tax_unit_non_dep_add(tax_unit, period, sources)
            disallowed_losses = disallowed_losses + max_(0, -net_income - p.loss_limit)
        # Adjusted gross income deducts the business, farm, rental and Form
        # 4797 losses only up to the section 461(l) limit. The excess business
        # loss was never deducted, so it is not added back.
        excess_business_loss = tax_unit("excess_business_loss", period)
        return max_(0, disallowed_losses - excess_business_loss)

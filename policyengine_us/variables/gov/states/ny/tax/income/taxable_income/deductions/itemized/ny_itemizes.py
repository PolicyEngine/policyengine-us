from policyengine_us.model_api import *


def get_ny_itemization_branch(tax_unit, period, itemizes: bool):
    """
    The branch of ``tax_unit``'s simulation that fixes ``ny_itemizes``.

    With the election an input, the branch calculates New York taxes without
    calling the ``ny_itemizes`` formula that asks for them.
    """
    return get_override_branch(
        tax_unit.simulation,
        "ny_itemizing" if itemizes else "ny_not_itemizing",
        period,
        {"ny_itemizes": np.full(tax_unit.count, itemizes, dtype=bool)},
    )


class ny_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Itemizes New York deductions"
    documentation = (
        "Whether the tax unit takes the New York itemized deduction rather "
        "than the New York standard deduction. Among filers who may itemize "
        "(before 2018, only federal itemizers), it itemizes when that gives "
        "less New York State plus New York City income tax, counting the "
        "college tuition credit given up by itemizing. A tie takes the "
        "standard deduction."
    )
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/613",
        # N.Y. Tax Law 615(a), current text (supports the 2018 rule).
        "https://legislation.nysenate.gov/pdf/laws/TAX615",
        # 2017 Form IT-201 instructions, line 34 (supports the 2017 rule).
        "https://www.tax.ny.gov/pdf/2017/inc/it201i_2017.pdf#page=20",
        # 2018 Form IT-196 instructions, New for 2018 (p. 1).
        "https://www.tax.ny.gov/pdf/2018/inc/it196i_2018.pdf#page=1",
        # 2025 Form IT-201 instructions, line 34, whose note gives the choice
        # of a college tuition credit or itemized deduction.
        "https://www.tax.ny.gov/forms/html-instructions/2025/it/it201i-2025.htm#step-5",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.deductions.itemized
        # Values both choices share, calculated before branching so that
        # both branches inherit them rather than recalculate them. Federal
        # itemizing is not among them: the federal deduction for state and
        # local taxes adds New York City income tax, which follows this
        # election, so the federal choice is not calculated here.
        tax_unit("ny_agi", period)
        tax_unit("ny_standard_deduction", period)
        tax_unit("ny_itemized_deductions", period)
        tax_unit("ny_allowable_college_tuition_expenses", period)
        itemizing = get_ny_itemization_branch(tax_unit, period, itemizes=True)
        if p.federal_itemization_required:
            # Before 2018, N.Y. Tax Law 615(a) lets only a filer who itemized
            # federally elect the New York itemized deduction. The federal
            # choice is the one made when New York itemizes, as it is taken
            # from the branch where New York itemizes.
            may_itemize = itemizing.calculate("tax_unit_itemizes", period)
            if not may_itemize.any():
                return may_itemize
        else:
            may_itemize = np.ones(tax_unit.count, dtype=bool)
        not_itemizing = get_ny_itemization_branch(tax_unit, period, itemizes=False)
        # The election moves New York taxable income, which New York City
        # taxable income adds, and it decides the college tuition credit, so
        # the choices are compared on State plus City tax. The Yonkers
        # resident surcharge is a fixed share of State tax, so it cannot
        # change which choice costs less.
        taxes = ["ny_income_tax", "nyc_income_tax"]
        tax_if_itemizing = sum(itemizing.calculate(tax, period) for tax in taxes)
        tax_if_not_itemizing = sum(
            not_itemizing.calculate(tax, period) for tax in taxes
        )
        # Itemize only when it saves more than a rounding error: a tie takes
        # the standard deduction, which keeps the college tuition credit.
        TOLERANCE = 0.01
        return may_itemize & (tax_if_itemizing < tax_if_not_itemizing - TOLERANCE)

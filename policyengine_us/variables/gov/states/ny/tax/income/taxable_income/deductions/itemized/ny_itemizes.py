from policyengine_us.model_api import *

# The State and City tax the election can move. Tax before refundable
# credits is tax before credits less the non-refundable credits, which tax
# before credits caps.
TAXES_THE_ELECTION_MOVES = [
    "ny_income_tax_before_refundable_credits",
    "nyc_income_tax_before_refundable_credits",
]
# The refundable credits that follow the election.
CREDITS_THE_ELECTION_MOVES = [
    # Itemizing gives up the college tuition credit.
    "ny_college_tuition_credit",
    # The school tax credit's rate reduction amount is a schedule of City
    # taxable income.
    "nyc_school_tax_credit",
    # The City income tax elimination credit is a share of City tax before
    # refundable credits, less the City EITC and child care credit.
    "nyc_income_tax_elimination_credit",
]
# The New York EITC is reduced by the household credit allowed, which tax
# before credits caps, and the supplemental EITC is a share of the EITC. The
# election moves them only where it moves the household credit allowed.
EITCS_THE_ELECTION_MOVES = ["ny_eitc", "ny_supplemental_eitc"]


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


def tax_the_election_moves(branch, period, credits):
    """
    The New York State and City tax in ``branch`` that the election can move:
    tax before refundable credits, less ``credits``.

    It leaves out the credits the election moves only through federal tax,
    such as the Empire State child credit, so the branch does not
    recalculate federal tax.
    """
    tax = sum(branch.calculate(name, period) for name in TAXES_THE_ELECTION_MOVES)
    return tax - sum(branch.calculate(name, period) for name in credits)


class ny_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Itemizes New York deductions"
    documentation = (
        "Whether the tax unit takes the New York itemized deduction rather "
        "than the New York standard deduction. Among filers who may itemize "
        "(before 2018, only federal itemizers), a filer with college tuition "
        "expenses itemizes when that gives less New York State plus New York "
        "City income tax, counting the college tuition credit given up by "
        "itemizing, and a tie takes the standard deduction. A filer without "
        "them gives up no credit by itemizing, and itemizes when the "
        "itemized deduction is larger."
    )
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/613",
        # N.Y. Tax Law 615(a), current text (supports the 2018 rule), and
        # 615(d)(4), where the Legislature allows no college tuition itemized
        # deduction to a filer who claims the college tuition credit.
        "https://legislation.nysenate.gov/pdf/laws/TAX615",
        # L.2018 ch. 59, Part JJ, sections 3 and 7: the Legislature amends
        # 615(a) for taxable years from 2018 (supports both rules).
        "https://legislation.nysenate.gov/pdf/bills/2017/S7509C#page=42",
        # 2017 Form IT-201 instructions, line 34 (supports the 2017 rule).
        "https://www.tax.ny.gov/pdf/2017/inc/it201i_2017.pdf#page=20",
        # 2018 Form IT-196 instructions, New for 2018.
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
        standard = tax_unit("ny_standard_deduction", period)
        itemized = tax_unit("ny_itemized_deductions", period)
        tuition = tax_unit("ny_allowable_college_tuition_expenses", period)
        if p.federal_itemization_required:
            # Before 2018, N.Y. Tax Law 615(a) lets only a filer who itemized
            # federally elect the New York itemized deduction. The federal
            # choice is the one made when New York itemizes, as it is taken
            # from the branch where New York itemizes.
            itemizing = get_ny_itemization_branch(tax_unit, period, itemizes=True)
            may_itemize = itemizing.calculate("tax_unit_itemizes", period)
            if not may_itemize.any():
                return may_itemize
        else:
            may_itemize = np.ones(tax_unit.count, dtype=bool)
        larger = itemized > standard
        # Without college tuition expenses, itemizing gives up no credit, so
        # the larger deduction gives no more tax. Only a filer with both a
        # larger itemized deduction and tuition expenses needs the taxes.
        trades_credit = may_itemize & larger & (tuition > 0)
        if not trades_credit.any():
            return may_itemize & larger
        itemizing = get_ny_itemization_branch(tax_unit, period, itemizes=True)
        not_itemizing = get_ny_itemization_branch(tax_unit, period, itemizes=False)
        # The election moves New York taxable income, which New York City
        # taxable income adds, and it decides the college tuition credit, so
        # the choices are compared on the State plus City tax they move. The
        # Yonkers resident surcharge is a fixed share of State tax, so it
        # cannot change which choice costs less.
        credits = list(CREDITS_THE_ELECTION_MOVES)
        # Where the household credit allowed is the same under both choices,
        # so is the New York EITC, and leaving it out of both sides spares
        # the branches its federal credit (in 2021, recalculated under the
        # law before the American Rescue Plan Act).
        household_credit_moves = itemizing.calculate(
            "ny_household_credit", period
        ) != not_itemizing.calculate("ny_household_credit", period)
        if (trades_credit & household_credit_moves).any():
            credits += EITCS_THE_ELECTION_MOVES
        tax_if_itemizing = tax_the_election_moves(itemizing, period, credits)
        tax_if_not_itemizing = tax_the_election_moves(not_itemizing, period, credits)
        # Itemize only when it saves more than a rounding error: a tie takes
        # the standard deduction, which keeps the college tuition credit.
        TOLERANCE = 0.01
        lower = tax_if_itemizing < tax_if_not_itemizing - TOLERANCE
        return may_itemize & where(trades_credit, lower, larger)

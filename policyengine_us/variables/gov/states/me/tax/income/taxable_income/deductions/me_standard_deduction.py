from policyengine_us.model_api import *


class me_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.mainelegislature.org/legis/statutes/36/title36sec111.html",
        "https://www.mainelegislature.org/legis/statutes/36/title36sec5124-C.html",
        "https://legislature.maine.gov/legis/bills/getPDF.asp?paper=HP1491&item=37&snum=132#page=138",
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/legischange26.pdf#page=9",
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # Maine conforms to the Internal Revenue Code as amended through
        # December 31, 2025 (36 M.R.S. Sec. 111(1-A)), but for tax years 2025
        # and 2026 Sec. 5124-C(1-B) and (1-C) set Maine's own basic standard
        # deduction amounts, which are lower than the federal amounts. From tax
        # year 2027 on, Sec. 5124-C(1-D) sets the Maine standard deduction equal
        # to the federal standard deduction.
        p = parameters(period).gov.states.me.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        aged_blind_count = tax_unit("aged_blind_count", period)
        me_amount = (
            p.amount[filing_status] + p.aged_or_blind[filing_status] * aged_blind_count
        )
        # From 2027 Maine takes the federal standard deduction itself, not a
        # re-addition of the federal basic and aged-or-blind parameters. Reading
        # the federal variable carries the rest of IRC Section 63(c): the zero
        # basic deduction for a separate filer whose spouse itemizes
        # (Section 63(c)(6)) and the cap for a filer who is a dependent of
        # another taxpayer (Section 63(c)(5)).
        return where(
            p.follows_federal,
            tax_unit("standard_deduction", period),
            me_amount,
        )

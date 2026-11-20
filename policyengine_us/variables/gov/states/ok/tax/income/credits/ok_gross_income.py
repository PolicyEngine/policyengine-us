from policyengine_us.model_api import *


class ok_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma gross household income for the sales tax and property tax credits"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Gross household income for the Oklahoma sales tax credit (Form 538-S) "
        "and property tax credit (Form 538-H): the income of every type, "
        "taxable or not, received by all persons occupying the same household. "
        "Each tax unit's own gross income is computed from the sources list, "
        "and every tax unit in a household gets the sum over all the tax units "
        "in that household, so co-residents who file their own returns count."
    )
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf",
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf",
        # 2025 Form 538-S, Part 3 (lines 1 to 14) and the definition of total
        # gross household income.
        # PDF pages 1-3
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-S.pdf#page=1",
        # 2025 Form 538-H, Part 2 (lines 1 to 14) and the definition of gross
        # household income.
        # PDF pages 1, 3
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-H.pdf#page=1",
        # 68 O.S. 2904(3) (property tax credit) and 68 O.S. 5012 (sales tax
        # credit) define gross household income.
        # PDF pages 1373, 1635
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os68.pdf#page=1373",
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-710-50-15-96",
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ok.tax.income
        # Each tax unit's own gross income, line by line as its own return
        # reports it. Capital gains are netted within the return before the
        # positive-only rule, as line 11 takes gains from the federal return.
        capital_gain_sources = [
            "short_term_capital_gains",
            "long_term_capital_gains",
        ]
        unit_income = max_(0, add(tax_unit, period, capital_gain_sources))
        for source in p.credits.gross_income_sources:
            if source in capital_gain_sources:
                continue
            # Gross income includes only positive amounts (i.e., no losses).
            unit_income = unit_income + max_(0, add(tax_unit, period, [source]))
        # 68 O.S. 5012 and 2904(3) count income "received by all persons
        # occupying the same household", as do OAC 710:50-15-96(c), Form
        # 538-S Part 3 (line 13: "income of others living in your
        # household") and Form 538-H Part 2. Spread each tax unit's amount
        # evenly over its members, sum the members of each household, and
        # give each tax unit its household's total. This maps through
        # persons, so tax units that share a household each count every
        # unit's income once.
        person = tax_unit.members
        member_share = tax_unit.project(unit_income / tax_unit.nb_persons())
        household_income = person.household.sum(member_share)
        return tax_unit.value_from_first_person(household_income)

from policyengine_us.model_api import *


class state_sales_tax_income_bracket(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "State Sales Tax Income Bracket"
    documentation = (
        "The Optional State Sales Tax Table income row for the filers' income: "
        "their adjusted gross income plus their own nontaxable items. A tax "
        "unit dependent's benefits and nontaxable income, such as a child's "
        "Social Security or SSI, are the dependent's own and stay out. TANF is "
        "an SPM unit amount, so every tax unit member's per-person share of it "
        "counts, the dependents' included."
    )
    reference = (
        # "Your 2025 income is the amount shown on your Form 1040 or 1040-SR,
        # line 11b, plus any nontaxable items".
        "https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=5",
        # IRS Pub. 915 (2025), "Who is taxed": benefits are income of "the
        # person who has the legal right to receive the benefits".
        "https://www.irs.gov/pub/irs-prior/p915--2025.pdf#page=5",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.deductions.itemized.salt_and_real_estate.state_sales_tax_table
        # Person-level items are summed over the head and spouse. Tax-unit
        # sources (adjusted gross income, the filers' nontaxable Social
        # Security) are the filers' own already, and SPM-unit TANF is added
        # as each member's per-person share.
        income = tax_unit_non_dep_add(tax_unit, period, p.income_sources)
        return p.income_bracket.calc(income)

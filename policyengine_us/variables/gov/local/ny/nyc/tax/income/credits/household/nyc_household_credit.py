from policyengine_us.model_api import *


class nyc_household_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC Household Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/1310",
        "https://www.tax.ny.gov/pdf/2025/inc/it201i_2025.pdf#page=13",
    )

    def formula(tax_unit, period, parameters):
        # First get their federal AGI.
        # Technically based on recomputed AGI, which deviates slightly from federal AGI.
        federal_agi = tax_unit("adjusted_gross_income", period)

        # Then get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Then get the household credit part of the parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.household

        filing_statuses = filing_status.possible_values

        # Tax Law 1310(d) counts the exemptions each household is entitled to
        # and excludes, among unmarried individuals, one whom another taxpayer
        # can claim; a husband and wife, a head of household and a surviving
        # spouse are households in their own right. IT-201 line 48 says "If
        # you marked the Yes box at item C ... you do not qualify for this
        # credit" for every return; the model follows the statute.
        dependent_filer = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        single = filing_status == filing_statuses.SINGLE
        exemptions = tax_unit("exemptions_count", period)
        # A husband and wife filing separately are one household: 1310(d)
        # aggregates "their federal adjusted gross incomes ... irrespective
        # of whether joint or separate city income tax returns are filed",
        # and each spouse gets "one-half the credit otherwise allowed his or
        # her household" (IT-201 Table 6: AGI and dependents "from both
        # returns", plus one for each spouse). The model has no record of the
        # other spouse's return, so it is assumed alike, as for New York
        # State: its AGI and its unit's size are added.
        separate_agi = federal_agi + tax_unit(
            "spouse_separate_adjusted_gross_income", period
        )
        separate_exemptions = exemptions + tax_unit(
            "spouse_separate_tax_unit_size", period
        )
        amount = select(
            [
                filing_status == filing_statuses.SINGLE,
                filing_status == filing_statuses.SEPARATE,
            ],
            [
                # Single filers get a flat amount.
                p.flat_amount.calc(federal_agi, right=True),
                # Separate filers get "one-half the credit otherwise allowed his
                # or her household": the married amount per exemption at the
                # couple's AGI, times the couple's exemptions, halved. IT-201
                # Table 6 instead rounds a per-exemption half amount, which can
                # differ by a dollar or more; the model follows the statute.
                p.other_per_dependent.calc(separate_agi, right=True)
                * separate_exemptions
                / 2,
            ],
            # Joint, head of household, and surviving spouse filers have a different
            # amount per exemption, varying with AGI.
            default=p.other_per_dependent.calc(federal_agi, right=True) * exemptions,
        )
        return where(dependent_filer & single, 0, amount)

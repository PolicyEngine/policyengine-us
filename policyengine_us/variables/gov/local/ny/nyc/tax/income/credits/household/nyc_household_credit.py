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
        amount = select(
            [
                filing_status == filing_statuses.SINGLE,
                filing_status == filing_statuses.SEPARATE,
            ],
            [
                # Single filers get a flat amount.
                p.flat_amount.calc(federal_agi, right=True),
                # Separate filers get an amount for each exemption, varying
                # with AGI.
                p.separate_per_dependent.calc(federal_agi, right=True) * exemptions,
            ],
            # Joint, head of household, and surviving spouse filers have a different
            # amount per exemption, varying with AGI.
            default=p.other_per_dependent.calc(federal_agi, right=True) * exemptions,
        )
        return where(dependent_filer & single, 0, amount)

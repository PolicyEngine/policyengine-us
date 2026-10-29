from policyengine_us.model_api import *


class nc_child_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina child deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC
    reference = (
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-153.5.html",
        # S.L. 2026-31, Section 12.(a), amending G.S. 105-228.90(b)(7).
        "https://www.ncleg.gov/EnactedLegislation/SessionLaws/PDF/2025-2026/SL2026-31.pdf#page=42",
        # 2025 Form D-401 instructions, Line 10a.
        "https://www.ncdor.gov/2025-d-401-individual-income-tax-instructions/open#page=13",
    )

    def formula(tax_unit, period, parameters):
        # calculate deduction amount per eligible child
        federal_agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        p = parameters(period).gov.states.nc.tax.income.deductions.child
        amount = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.JOINT,
                filing_status == statuses.SURVIVING_SPOUSE,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.single.calc(federal_agi, right=True),
                p.separate.calc(federal_agi, right=True),
                p.joint.calc(federal_agi, right=True),
                p.surviving_spouse.calc(federal_agi, right=True),
                p.head_of_household.calc(federal_agi, right=True),
            ],
        )
        # G.S. 105-153.5(a1) allows the deduction "for each qualifying child
        # for whom the taxpayer is allowed the federal tax credit" under
        # section 24 of the Code. S.L. 2026-31 moved the Code date in
        # G.S. 105-228.90(b)(7) from January 1, 2023 to July 5, 2025, so the
        # filer social security number rule that the One Big Beautiful Bill
        # Act added to IRC 24(h)(7) applies; ctc_qualifying_children counts
        # only children for whom the federal credit is allowed.
        # Unlike Utah ("a tax credit under Section 24") and Maine ("qualifying
        # child or dependent"), North Carolina counts only a qualifying child
        # for whom "the federal tax credit" is allowed. IRC 24(h)(4)(C) calls
        # a child that IRC 24(h)(7) excludes a "qualifying child with respect
        # to whom a credit is not allowed under this section", so the credit
        # for other dependents for that child does not count. The 2025 D-401
        # instructions for line 10a likewise ask for "the number of qualifying
        # children for whom you were allowed a federal child tax credit".
        children = tax_unit("ctc_qualifying_children", period)
        # calculate NC child deduction
        return amount * children

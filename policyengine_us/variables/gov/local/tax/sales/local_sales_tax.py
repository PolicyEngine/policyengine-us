from policyengine_us.model_api import *


class local_sales_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Local sales tax"
    unit = USD
    documentation = (
        "Local general sales taxes from the IRS sales tax deduction worksheet "
        "(line 6), for the optional sales tax deduction of 26 U.S.C. "
        "164(b)(5)(H): the Optional Local Sales Tax Table amount times the local "
        "rate in the states whose residents use those tables, and otherwise the "
        "state table amount times the local rate over the state rate."
    )
    reference = (
        # State and Local General Sales Tax Deduction Worksheet.
        "https://www.irs.gov/pub/irs-prior/i1040sca--2015.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2016.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2017.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2018.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2019.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2020.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2021.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2022.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2023.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2024.pdf#page=4",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=4",
        # Worksheet line 2 and 6 instructions.
        "https://www.irs.gov/pub/irs-prior/i1040sca--2022.pdf#page=6",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2023.pdf#page=6",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2024.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=5",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        state_code = tax_unit.household("state_code", period)
        state_code_str = tax_unit.household("state_code_str", period)
        # Line 3: the local general sales tax rate.
        local_rate = tax_unit.household("local_sales_tax_rate", period)
        # Line 4: the state rate in the state table heading.
        heading_rate = p.state_sales_tax_table.rate[state_code]
        # Line 2: the Optional Local Sales Tax Tables give the base local tax
        # for a 1% local rate, by the state table's income row and family size.
        table = tax_unit.household("local_sales_tax_table", period)
        TAX_UNIT_SIZE_CAP = 6
        tax_unit_size = tax_unit("tax_unit_size", period)
        family_size = max_(min_(tax_unit_size, TAX_UNIT_SIZE_CAP), 1).astype(int)
        income_bracket = max_(
            tax_unit("state_sales_tax_income_bracket", period), 1
        ).astype(int)
        base_local_tax = p.local_sales_tax_table.tax[table][family_size][income_bracket]
        # Line 6, "No" (line 2 is not 0): line 2 x line 3, with line 3 in
        # percentage points.
        table_amount = base_local_tax * local_rate / 0.01
        # Line 6, "Yes": line 1 x line 5, where line 5 = line 3 / line 4.
        ratio = np.divide(
            local_rate,
            heading_rate,
            out=np.zeros_like(local_rate),
            where=heading_rate > 0,
        )
        ratio_amount = tax_unit("state_sales_tax", period) * ratio
        uses_local_table = np.isin(state_code_str, p.local_sales_tax_table.states)
        # Full-year residents of these jurisdictions "skip lines 2 through 5,
        # enter -0- on line 6" of the worksheet.
        has_local_sales_tax = ~np.isin(
            state_code_str, p.state_sales_tax_table.no_local_sales_tax_states
        )
        return has_local_sales_tax * where(uses_local_table, table_amount, ratio_amount)

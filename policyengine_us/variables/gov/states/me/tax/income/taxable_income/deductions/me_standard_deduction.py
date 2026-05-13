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
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/25_1040me_gen_instr_w_cover_pg.pdf",
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # Maine conforms to the Internal Revenue Code as of December 31, 2024
        # (36 MRSA Sec. 111), so it did not adopt the One Big Beautiful Bill
        # Act (OBBBA) increase to the federal standard deduction starting in
        # 2025. Maine publishes its own Standard Deduction Chart in the Form
        # 1040ME instructions.
        p = parameters(period).gov.states.me.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        basic = p.amount[filing_status]
        additional = p.aged_or_blind[filing_status] * tax_unit(
            "aged_blind_count", period
        )
        return basic + additional

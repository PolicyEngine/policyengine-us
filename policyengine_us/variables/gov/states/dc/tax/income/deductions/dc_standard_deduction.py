from policyengine_us.model_api import *


class dc_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC standard deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC
    reference = (
        # 47-1803.03(c): when spouses file separate returns and one itemizes,
        # the standard deduction "shall be allowed to neither".
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1803.03#(c)",
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2025_D40_Book_082026_v1.pdf#page=13",
    )

    def formula(tax_unit, period, parameters):
        # Before 2025, DC conformed to federal standard deduction
        standard = add(
            tax_unit,
            period,
            ["basic_standard_deduction", "additional_standard_deduction"],
        )
        return where(tax_unit("separate_filer_itemizes", period), 0, standard)

    def formula_2025(tax_unit, period, parameters):
        # Starting 2025, DC established its own basic standard deduction
        # amounts per D-40 booklet (does not conform to OBBBA increases).
        # Additional standard deduction still matches federal.
        p = parameters(period).gov.states.dc.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        basic = p.amount[filing_status]
        additional = add(tax_unit, period, ["additional_standard_deduction"])
        return where(tax_unit("separate_filer_itemizes", period), 0, basic + additional)

from policyengine_us.model_api import *


class ky_modified_agi_if_separate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky modified gross income for the family size tax credit on the combined-separate path"
    unit = USD
    definition_period = YEAR
    reference = (
        # KRS 141.066(4): spouses filing separately on a combined return use
        # their combined modified gross income, treating a separately computed
        # amount below zero as zero.
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=49188",
        # Worksheet for modified gross income, lines (a)-(j).
        "https://revenue.ky.gov/Forms/740%20Packet%20Instructions.pdf#page=26",
    )
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # Worksheet lines (a)-(b) and (f)-(g): each column's federal and
        # Kentucky adjusted gross income, entering zero if zero or less.
        fed_agi = tax_unit.sum(max_(person("ky_federal_agi", period), 0))
        ky_agi = tax_unit.sum(max_(person("ky_agi", period), 0))
        # Lump sum distributions not included in either AGI (lines (d) and
        # (h)). Tax-exempt interest from other states' municipal bonds (line
        # (c)) is not modeled.
        lump_sum = tax_unit("form_4972_lumpsum_distributions", period)
        return max_(fed_agi + lump_sum, ky_agi + lump_sum)

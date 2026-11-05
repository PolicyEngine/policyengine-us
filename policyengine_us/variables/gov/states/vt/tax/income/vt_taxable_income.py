from policyengine_us.model_api import *


class vt_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont taxable income"
    unit = USD
    documentation = (
        "Before 2017 and from 2018, Vermont AGI less the Vermont standard "
        "deduction and personal exemptions. In 2017, federal taxable income with Vermont's "
        "additions and subtractions under former 32 V.S.A. § 5811(21)."
    )
    definition_period = YEAR
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf",
        # Former 32 V.S.A. § 5811(21), as amended by 2015 Vt. Acts No. 57, § 64.
        "https://legislature.vermont.gov/Documents/2016/Docs/ACTS/ACT057/ACT057%20As%20Enacted.pdf#page=89",
        # 2017 Vt. Acts No. 73, § 13a reproduces the former text; § 32(5)
        # changes the base from 2018. PDF pages 21-22, 59.
        "https://legislature.vermont.gov/Documents/2018/Docs/ACTS/ACT073/ACT073%20As%20Enacted.pdf#page=21",
        "https://web.archive.org/web/2018/https://tax.vermont.gov/sites/tax/files/documents/IN-111%20Instr-2017.pdf#page=5",
    )
    defined_for = StateCode.VT

    def formula_2017(tax_unit, period, parameters):
        # Federal taxable income before its zero floor, so that a negative
        # federal base offsets Vermont's additions.
        agi = tax_unit("adjusted_gross_income", period)
        exemptions = tax_unit("exemptions", period)
        deductions = tax_unit("taxable_income_deductions", period)
        federal_base = agi - exemptions - deductions
        additions = add(
            tax_unit,
            period,
            ["vt_2017_itemized_deduction_addback", "vt_2017_other_additions"],
        )
        subtractions = tax_unit("vt_2017_subtractions", period)
        return max_(0, federal_base + additions - subtractions)

    def formula_2018(tax_unit, period, parameters):
        agi = tax_unit("vt_agi", period)
        deductions = tax_unit("vt_standard_deduction", period)
        exemptions = tax_unit("vt_personal_exemptions", period)
        return max_(0, agi - deductions - exemptions)

    # Before 2017, keep the Vermont-base formula. Former § 5811(21) also set
    # the federal base for 2015 and 2016, which this variable doesn't model.
    formula = formula_2018

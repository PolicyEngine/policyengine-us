from policyengine_us.model_api import *


class ia_itemized_deductions_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa itemized deductions reduction for high-income filers"
    unit = USD
    definition_period = YEAR
    reference = (
        # 2018 IA 104 Iowa Itemized Deductions Worksheet.
        "https://revenue.iowa.gov/media/2335/download?inline=#page=1",
        # 701 IAC 41.11 (IAC 2/28/18), PDF pages 9-10.
        "https://www.legis.iowa.gov/docs/iac/chapter/03-28-2018.701.41.pdf#page=9",
        # Iowa Code 422.9(2) (2018).
        "https://www.legis.iowa.gov/docs/code/2018/422.9.pdf#page=1",
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ia.tax.income.deductions.itemized
        if not p.limitation.retained:
            return 0
        # IA 104 line 1: Iowa Schedule A lines 1 to 25.
        deductions = tax_unit("ia_itemized_deductions_pre_limitation", period)
        # IA 104 line 2: Iowa income tax on federal Schedule A line 5a, which
        # holds state income taxes only when they exceed sales taxes.
        income_taxes = add(
            tax_unit, period, ["state_withheld_income_tax", "local_income_tax"]
        )
        sales_taxes = add(tax_unit, period, ["state_sales_tax", "local_sales_tax"])
        iowa_income_tax = where(
            income_taxes >= sales_taxes,
            add(tax_unit, period, ["ia_withheld_income_tax"]),
            0,
        )
        # IA 104 line 4: medical expenses, investment interest, and casualty,
        # theft and gambling losses, which section 68(c) leaves unlimited.
        p_fed = parameters(period).gov.irs.deductions.itemized.limitation
        excluded = add(tax_unit, period, p_fed.excluded_deductions)
        # IA 104 lines 3 and 5. Lines 3 to 11 run in float64, so float32 error
        # can't move line 18 across a half.
        reducible = max_(0, deductions + iowa_income_tax - excluded).astype(np.float64)
        # IA 104 lines 7 to 9, with the federal filing status.
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        excess_agi = max_(
            0, agi - p.limitation.applicable_amount[filing_status]
        ).astype(np.float64)
        # IA 104 lines 6, 10 and 11.
        reduction = min_(
            p.limitation.itemized_deduction_rate * reducible,
            p.limitation.agi_rate * excess_agi,
        )
        # IA 104 lines 12 to 21 subtract the Iowa income tax in the share of
        # line 5 that the reduction leaves. Line 18 enters that share to the
        # nearest tenth of a percent; neither Iowa Code 422.9(2) nor 701 IAC
        # 41.11(1) says how to round it. So line 1 - line 21 =
        # line 11 - line 2 * (1 - line 18), which can fall slightly below 0.
        share = np.divide(
            reducible - reduction,
            reducible,
            out=np.ones_like(reducible),
            where=reducible > 0,
        )
        # A half rounds up; the offset absorbs float64 error.
        line_18 = np.floor(share * 1_000 + 0.5 + 1e-9) / 1_000
        return reduction - iowa_income_tax * (1 - line_18)

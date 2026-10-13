from policyengine_us.model_api import *


class mn_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-12/m1_21_0.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2023-12/m1_inst_21.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2023-12/m1_22.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2024-02/m1-inst-22.pdf",
        # 2024 Schedule M1SA, line 19, and the line 26 limitation worksheets
        # PDF pages 1, 8
        "https://www.revenue.state.mn.us/sites/default/files/2024-12/m1sa-24.pdf#page=1",
        # Minn. Stat. § 290.0122, subd. 2(d) and subd. 8
        "https://www.revisor.mn.gov/statutes/cite/290.0122",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        # 2021 Form M1 instructions say:
        #   You may claim the Minnesota standard deduction or itemize
        #   your deductions on your Minnesota return. You will generally
        #   pay less Minnesota income tax if you take the larger of your
        #   itemized or standard deduction.
        # ... calculate pre-limitation itemized deductions
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)
        capped_property_taxes = tax_unit("capped_property_taxes", period)
        # Schedule M1SA line 19 takes Minnesota's own casualty and theft loss
        # (Schedule M1CAT) in place of the federal one, which is limited to
        # declared disasters from 2018.
        federal_casualty_loss = tax_unit("casualty_loss_deduction", period)
        mn_casualty_loss = tax_unit("mn_casualty_loss_deduction", period)
        mn_itm_deds = (
            itm_deds_less_salt
            - federal_casualty_loss
            + mn_casualty_loss
            + capped_property_taxes
        )
        # ... calculate itemized deductions offset
        p = parameters(period).gov.states.mn.tax.income.deductions.itemized
        # Minn. Stat. 290.0122, subd. 2(d), and the M1SA line 26 worksheets
        # (step 2: lines 4, 13 and 19) leave medical expenses and casualty
        # and theft losses out of the reduction.
        exempt_deds = add(
            tax_unit,
            period,
            ["medical_expense_deduction", "mn_casualty_loss_deduction"],
        )
        net_deds = max_(0, mn_itm_deds - exempt_deds)
        filing_status = tax_unit("filing_status", period)
        lower_reduction_rate = p.reduction.excess_agi_fraction.low
        lower_reduction_threshold = p.reduction.agi_threshold.low[filing_status]
        agi = tax_unit("adjusted_gross_income", period)
        lower_excess = max_(0, agi - lower_reduction_threshold)
        alternate_reduction_amount = p.reduction.alternate.rate * net_deds
        if p.alternate_reduction_applies:
            higher_reduction_threshold = p.reduction.agi_threshold.high[filing_status]

            spread = higher_reduction_threshold - lower_reduction_threshold
            lower_reduction_amount = lower_reduction_rate * min_(lower_excess, spread)
            higher_reduction_rate = p.reduction.excess_agi_fraction.high
            higher_excess = max_(0, agi - higher_reduction_threshold)
            higher_reduction_amount = higher_reduction_rate * higher_excess
            main_reduction_amount = lower_reduction_amount + higher_reduction_amount
            alternate_reduction_applies = agi > p.reduction.alternate.income_threshold
            smaller_reduction_amount = min_(
                alternate_reduction_amount, main_reduction_amount
            )
            reduction = where(
                alternate_reduction_applies,
                alternate_reduction_amount,
                smaller_reduction_amount,
            )
        else:
            # ... calculate pre-limitation amount
            excess_agi = max_(0, agi - lower_reduction_threshold)
            main_reduction_amount = lower_reduction_rate * excess_agi
            reduction = min_(alternate_reduction_amount, main_reduction_amount)
        return max_(0, mn_itm_deds - reduction)

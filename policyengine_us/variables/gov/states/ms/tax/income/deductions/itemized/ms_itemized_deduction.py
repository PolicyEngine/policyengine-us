from policyengine_us.model_api import *


class ms_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi itemized deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        # compute itemized deduction maximum
        p = parameters(period).gov.irs.deductions
        itm_deds = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["salt_deduction"]
        ]
        itm_deds_less_salt = add(tax_unit, period, itm_deds)
        filing_status = tax_unit("filing_status", period)
        # uncapped_property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        # itm_deds_max = itm_deds_less_salt + uncapped_property_taxes

        # calculate itemized deductions total amount
        p = parameters(period).gov.states.ms.tax.income.deductions.itemized
        exempt_deds = add(
            tax_unit,
            period,
            [
                "medical_expense_deduction",
                "casualty_loss_deduction",
                "itemized_taxable_income_deductions",
                "interest_deduction",
                "charitable_contribution",
                "misc_deduction",
            ],
        )
        net_deds = max_(0, exempt_deds)
        # net_deds_offset = p.deduction_fraction * net_deds # what is deduction_fraction

        agi = tax_unit("adjusted_gross_income", period)  # why use pe's agi
        excess_agi = max_(0, agi - p.agi_threshold[filing_status])

        # excess_agi_offset = p.excess_agi_fraction * excess_agi
        offset = min_(net_deds, excess_agi)
        return max_(0, offset)

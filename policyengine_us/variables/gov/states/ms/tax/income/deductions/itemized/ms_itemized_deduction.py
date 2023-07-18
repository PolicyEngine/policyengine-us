from policyengine_us.model_api import *


class ms_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi itemized deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    references = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf"
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80108228.pdf"
    )

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

        agi = tax_unit("adjusted_gross_income", period)
        # excess_agi = max_(0, agi - p.agi_threshold[filing_status])

        return max_(0, exempt_deds)

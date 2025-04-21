from policyengine_us.model_api import *


class taxable_income_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable income deductions"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        deductions_if_itemizing = tax_unit(
            "taxable_income_deductions_if_itemizing", period
        )
        deductions_if_not_itemizing = tax_unit(
            "taxable_income_deductions_if_not_itemizing", period
        )
        # Limiting itemized deductions to taxable income, if itemizing
        p = parameters(period).gov.simulation
        if p.limit_itemized_deductions_to_taxable_income:
            agi = tax_unit("adjusted_gross_income", period)
            exemptions = tax_unit("exemptions", period)
            itemizes = tax_unit("tax_unit_itemizes", period)
            agi_less_exemptions = max_(0, agi - exemptions)
            capped_deductions_if_itemizing = min_(
                deductions_if_itemizing, agi_less_exemptions
            )
            return where(
                itemizes,
                capped_deductions_if_itemizing,
                deductions_if_not_itemizing,
            )
        return where(
            itemizes, deductions_if_itemizing, deductions_if_not_itemizing
        )

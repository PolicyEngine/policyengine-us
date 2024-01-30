from policyengine_us.model_api import *


class de_income_tax_before_non_refundable_credits_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Delaware personal income tax before non-refundable credits combined"
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        filing_separately = tax_unit("de_files_separately", period)
        itax_indiv = add(
            tax_unit,
            period,
            ["de_income_tax_before_non_refundable_credits_indv"],
        )
        itax_joint = add(
            tax_unit,
            period,
            ["de_income_tax_before_non_refundable_credits_joint"],
        )

        return where(filing_separately, itax_indiv, itax_joint)

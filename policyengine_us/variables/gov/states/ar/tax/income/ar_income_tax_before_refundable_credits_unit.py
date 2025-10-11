from policyengine_us.model_api import *


class ar_income_tax_before_refundable_credits_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        filing_separately = tax_unit("ar_files_separately", period)
        itax_indiv = add(
            tax_unit,
            period,
            ["ar_income_tax_before_refundable_credits_indiv"],
        )
        itax_joint = add(
            tax_unit,
            period,
            ["ar_income_tax_before_refundable_credits_joint"],
        )

        return where(filing_separately, itax_indiv, itax_joint)

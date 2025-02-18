from policyengine_us.model_api import *


class amt_excluded_deductions(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AMT taxable income excluded deductions"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/55#b_2"

    def formula(tax_unit, period, parameters):
        itemizing = tax_unit("tax_unit_itemizes", period)
        standard_deduction = tax_unit("standard_deduction", period)
        salt_deduction = tax_unit("salt_deduction", period)
        # After TCJA expiration, miscellaneous deductions are added back to the AMTI
        if period.start.year >= 2026:
            misc_deduction = tax_unit("misc_deduction", period)
            return where(
                itemizing, salt_deduction + misc_deduction, standard_deduction
            )

        return where(itemizing, salt_deduction, standard_deduction)

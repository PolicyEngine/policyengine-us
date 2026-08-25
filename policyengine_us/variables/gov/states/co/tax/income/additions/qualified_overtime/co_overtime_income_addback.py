from policyengine_us.model_api import *


class co_overtime_income_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado overtime compensation deduction add-back"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://content.leg.colorado.gov/sites/default/files/2025a_1296_signed.pdf",
        "https://tax.colorado.gov/individual-income-tax-guide",
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        # HB25-1296 (2025) decouples Colorado from the federal overtime deduction
        # (IRC 225), adding it back to federal taxable income for tax years
        # beginning on or after January 1, 2026. Colorado still conforms to the
        # federal tips deduction (IRC 224), so tips are not added back.
        in_effect = parameters(
            period
        ).gov.states.co.tax.income.additions.qualified_overtime.in_effect
        return in_effect * tax_unit("overtime_income_deduction", period)

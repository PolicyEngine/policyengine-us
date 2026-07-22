from policyengine_us.model_api import *


class mi_qualified_tips_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan qualified tips deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://legislature.mi.gov/Bills/Bill?ObjectName=2025-HB-4961",
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/treasury/reference/taxpayer-notices/notice-regarding-new-deductions-for-qualified-overtime-compensation-and-qualified-tips",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        # Public Act 24 of 2025 incorporates the federal IRC section 224 definition;
        # the Michigan deduction mirrors the qualified tips deducted on the federal
        # return, and applies only in tax years 2026-2028.
        in_effect = parameters(
            period
        ).gov.states.mi.tax.income.deductions.qualified_tips_and_overtime.in_effect
        return in_effect * tax_unit("tip_income_deduction", period)

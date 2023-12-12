from policyengine_us.model_api import *


class la_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana itemized deduction"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf#page=2",  # 2022 line 8B-line 8C
        "https://revenue.louisiana.gov/TaxForms/IT540i(2021)%20Instructions.pdf#page=3",  # 2021 line 8A-line 8C
        "https://www.legis.la.gov/Legis/Law.aspx?d=101760",  # (3)
    ]
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.la.tax.income.deductions.itemized.medical_expenses.exceedance
        p_us = parameters(period).gov.irs.deductions
        us_itemizing = tax_unit("tax_unit_itemizes", period)
        us_itemized_deduction = (
            tax_unit("itemized_deductions_less_salt", period) * us_itemizing
        )
        us_standard_deduction = tax_unit("standard_deduction", period)
        reduced_itm_deductions = max_(
            0, us_itemized_deduction - us_standard_deduction
        )
        medical_expenses = add(tax_unit, period, ["medical_expense"])
        if p.availability:
            return (
                max_(medical_expenses - us_standard_deduction, 0) * p.rate
            )  # 2022 itemized deductions
        else:
            return reduced_itm_deductions  # 2021 itemized deductions

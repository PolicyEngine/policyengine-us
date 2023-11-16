from policyengine_us.model_api import *


class la_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana itemized deduction"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf",
        "https://www.legis.la.gov/Legis/Law.aspx?d=101760",  # (3)
    ]
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.la.tax.income.deductions.itemized.medical
        p_us = parameters(period).gov.irs.deductions
        us_itemizing = tax_unit("tax_unit_itemizes", period)
        federal_itemized_deduction = (
            tax_unit("itemized_deductions_less_salt", period) * us_itemizing
        )
        federal_standard_deduction = tax_unit("standard_deduction", period)
        reduced_itm_deductions = max_(
            0, federal_itemized_deduction - federal_standard_deduction
        )  # 2021
        medical_expenses = (
            add(tax_unit, period, ["medical_expense"]) * us_itemizing
        )
        reduced_medical_expenses = (
            max_(medical_expenses - federal_standard_deduction, 0)
            * p.exceedance
        )  # 2022
        return where(
            p.medical_expense_exceedance_calculation,
            reduced_medical_expenses,
            reduced_itm_deductions,
        )

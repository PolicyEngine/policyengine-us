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
        p = parameters(period).gov.states.la.tax.income.deductions.itemized
        itemizes = tax_unit("tax_unit_itemizes", period)
        medical_expenses = add(tax_unit, period, ["medical_expense"])
        return (
            itemizes
            * max_(
                medical_expenses - tax_unit("standard_deduction", period), 0
            )
            * p.exceedance
        )

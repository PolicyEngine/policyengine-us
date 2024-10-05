from policyengine_us.model_api import *


class la_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf#page=2",  # 2022 line 8B-line 8C
        "https://revenue.louisiana.gov/TaxForms/IT540i(2021)%20Instructions.pdf#page=3",  # 2021 line 8A-line 8C
        "https://www.legis.la.gov/Legis/Law.aspx?d=101760",  # (3)
    ]
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.la.tax.income.deductions.itemized
        federal_standard_deduction = tax_unit("standard_deduction", period)
        # Louisiana limits the itemized deductions to the amount of either the federal medical
        # expense deduction or the total federal itemized deductions
        # less the federal standard deduction
        relevant_itemized_deductions = add(
            tax_unit, period, p.relevant_federal_deductions
        )
        reduced_relevant_itemized_deductions = max_(
            relevant_itemized_deductions - federal_standard_deduction, 0
        )
        return reduced_relevant_itemized_deductions * p.excess_fraction

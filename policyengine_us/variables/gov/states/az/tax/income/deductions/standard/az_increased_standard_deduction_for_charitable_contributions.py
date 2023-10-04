from policyengine_us.model_api import *


class az_increased_standard_deduction_for_charitable_contributions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona increased standard deduction for charitable contributions"
    unit = USD
    documentation = "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01041.htm"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.deductions.standard.increased
        charitable_deduction = tax_unit("charitable_deduction", period)
        charitable_contributions_credit = tax_unit(
            "az_charitable_contributions_credit", period
        )
        charitable_deduction_after_credit = max_(
            charitable_deduction - charitable_contributions_credit, 0
        )
        return p.rate * charitable_deduction_after_credit

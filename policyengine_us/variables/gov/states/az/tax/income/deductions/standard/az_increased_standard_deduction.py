from policyengine_us.model_api import *


class az_increased_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona increased standard deduction"
    unit = USD
    documentation = "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01041.htm"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.deductions.standard
        increased_percent = p.increased_percent
        az_charitable_contributions_credit = tax_unit(
            "az_charitable_contributions_credit", period
        )
        return increased_percent * az_charitable_contributions_credit

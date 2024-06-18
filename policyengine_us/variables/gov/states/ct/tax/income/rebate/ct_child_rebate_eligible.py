from policyengine_us.model_api import *


class ct_child_tax_rebate_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Connecticut child tax rebate"
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("ct_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ct.tax.income.rebate

        return p.income_limit[filing_status] >= taxable_income

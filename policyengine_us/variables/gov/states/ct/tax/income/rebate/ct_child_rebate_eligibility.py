from policyengine_us.model_api import *


class ct_child_tax_rebate_eligibility(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Connecticut child tax rebate eligibility"
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("ct_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ct.tax.income.rebate

        income_eligibility = p.limit[filing_status] >= taxable_income

        dependent_eligibility = (
            tax_unit("tax_unit_count_dependents", period) > 0
        )

        return income_eligibility & dependent_eligibility

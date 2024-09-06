from policyengine_us.model_api import *


class ri_child_tax_rebate_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Rhode Island Child Tax Rebate"
    definition_period = YEAR
    reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-08/H7123Aaa_CTR_0.pdf"
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.ri.tax.income.credits.child_tax_rebate.limit
        return income <= p.income[filing_status]

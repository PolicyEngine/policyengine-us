from policyengine_us.model_api import *


class child_tax_rebates(Variable):
    value_type = float
    entity = TaxUnit
    label = "RI Child Tax Rebates"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%201041%20Schedule%20M_w.pdf"
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        child_count = tax_unit("eitc_child_count", period)
        p = parameters(
            period
        ).gov.states.ri.tax.income.adjusted_gross_income.subtractions
        rebates = where(
            income <= p.child_tax_rebates.child_tax_rebates_cap[filing_status]
            and child_count <= p.child_tax_rebates.max_child,
            child_count * p.child_tax_rebates.child_tax_rebates_amount,
            0,
        )
        return rebates

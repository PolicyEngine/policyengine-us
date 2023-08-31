from policyengine_us.model_api import *


class ri_child_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island Child Tax Rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-08/H7123Aaa_CTR_0.pdf"
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        age = person("age", period)
        dependent = person("is_tax_unit_dependent", period)
        p = parameters(
            period
        ).gov.states.ri.tax.income.adjusted_gross_income.subtractions
        eligible_child_age = age <= p.child_tax_rebates.eligible_age
        eligible_child = eligible_child_age & dependent
        child_count = tax_unit.sum(eligible_child)
        max_eligible = (
            income <= p.child_tax_rebates.income_threshold[filing_status]
            and child_count >= p.child_tax_rebates.max_child
        )

        max_rebate = p.child_tax_rebates.max_child * p.child_tax_rebates.amount

        base_eligible = (
            income <= p.child_tax_rebates.income_threshold[filing_status]
        )

        base_rebate = where(
            base_eligible, child_count * p.child_tax_rebates.amount, 0
        )

        return where(
            max_eligible,
            max_rebate,
            base_rebate,
        )

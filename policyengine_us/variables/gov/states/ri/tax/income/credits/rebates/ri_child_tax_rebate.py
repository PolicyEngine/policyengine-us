from policyengine_us.model_api import *


class ri_child_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island Child Tax Rebate"
    documentation = (
        "One-time Rhode Island child tax rebate enacted and paid in 2022 and "
        "determined from the 2021 return. PolicyEngine attributes it to eligibility "
        "tax year 2021 through ri_refundable_credits. This variable is zero in other "
        "years."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-08/H7123Aaa_CTR_0.pdf"
    )
    defined_for = "ri_child_tax_rebate_eligible"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age = person("age", period)
        dependent = person("is_tax_unit_dependent", period)
        p = parameters(period).gov.states.ri.tax.income.credits.child_tax_rebate
        age_eligibility = age <= p.limit.age
        eligible_child = age_eligibility & dependent
        child_count = tax_unit.sum(eligible_child)
        capped_children = min_(child_count, p.limit.child)
        return capped_children * p.amount

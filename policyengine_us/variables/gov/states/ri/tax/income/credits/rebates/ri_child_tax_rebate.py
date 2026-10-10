from policyengine_us.model_api import *


class ri_child_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island Child Tax Rebate"
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
        # R.I. Gen. Laws 44-30-103(b)(1) pays the rebate for each child "whom
        # the eligible taxpayer validly claims as a dependent" on the 2021
        # return. Under IRC 152(b)(1) a return on which the filer (or, if
        # joint, either spouse) can be claimed as a dependent has none.
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        eligible_child = age_eligibility & dependent & ~filer_is_dependent
        child_count = tax_unit.sum(eligible_child)
        capped_children = min_(child_count, p.limit.child)
        return capped_children * p.amount

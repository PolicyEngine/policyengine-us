from policyengine_us.model_api import *


class nj_ctc_qualifying_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "New Jersey child tax credit qualifying children"
    unit = "child"
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-17-1/",
        "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=46",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.credits.ctc
        person = tax_unit.members
        age_eligible = person("age", period) < p.age_limit
        dependent = person("is_tax_unit_dependent", period)
        return tax_unit.sum(age_eligible & dependent)

from policyengine_us.model_api import *


class ne_refundable_ctc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Nebraska refundable Child Tax Credit eligible child"
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/about/2023-nebraska-legislative-changes"
    )
    defined_for = StateCode.NE

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.credits.ctc.refundable
        is_dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        age_eligible = age <= p.age_threshold
        has_childcare_expenses = (
            person.spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
            > 0
        )
        return is_dependent & age_eligible & has_childcare_expenses

from policyengine_us.model_api import *


class ar_medicaid_work_requirement_subject(Variable):
    value_type = bool
    entity = Person
    label = "Subject to the Arkansas historical Medicaid work requirement approximation"
    definition_period = YEAR
    reference = (
        "https://www.medicaid.gov/medicaid/section-1115-demo/demonstration-and-waiver-list/81021",
        "https://www.kff.org/medicaid/issue-brief/state-data-for-medicaid-work-requirements-in-arkansas/",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.dhs.medicaid.work_requirements
        category = person("medicaid_category", period)
        adult_group = category == category.possible_values.ADULT
        state = person.household("state_code_str", period)
        age = person("age", period)
        income_level = person("medicaid_income_level", period)
        age_subject = p.age_range.calc(age)
        income_subject = income_level <= p.income_limit
        return (
            (state == "AR")
            & p.applies
            & adult_group
            & age_subject
            & income_subject
        )

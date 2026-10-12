from policyengine_us.model_api import *


class mt_child_dependent_care_expense_deduction_qualifying_individual(Variable):
    value_type = bool
    entity = Person
    label = (
        "Qualifying individual for the Montana child dependent care expense deduction"
    )
    definition_period = YEAR
    reference = (
        "https://mca.legmt.gov/bills/2019/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
        "https://web.archive.org/web/20230914140156/https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/2441-M_2022.pdf#page=2",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.child_dependent_care_expense
        age = person("age", period)
        dependent = person("is_tax_unit_dependent", period)
        spouse = person("is_tax_unit_spouse", period)
        eligible_child = dependent & (age < p.age_limit)
        # MCA 15-30-2131(1)(c)(i)(B)-(C) waives the age limit for a
        # dependent unable to provide self-care because of physical or
        # mental illness and includes a spouse who is unable to provide
        # self-care.
        incapable_of_self_care = person("is_incapable_of_self_care", period)
        eligible_adult = (dependent | spouse) & incapable_of_self_care
        return eligible_child | eligible_adult

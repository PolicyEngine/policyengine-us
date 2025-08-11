from policyengine_us.model_api import *


class pr_exemptions_is_eligible_student(Variable):
    value_type = bool
    entity = Person
    label = "Puerto Rico dependent exemption eligible student"
    reference = "https://hacienda.pr.gov/sites/default/files/inst_individuals_2023.pdf#page=28"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR

    def formula(person, period, parameters):
        # Gross income limit is $7500 for a student dependent
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.exemptions.dependent
        is_dependent = person("pr_is_tax_unit_dependent", period)
        is_student = person("is_full_time_college_student", period)
        gross_income = person("pr_gross_income_person", period)
        age = person("age", period)
        age_eligibility = age < p.age_threshold.student
        income_eligibility = gross_income < p.income_limit.student
        return is_dependent & is_student & income_eligibility & age_eligibility

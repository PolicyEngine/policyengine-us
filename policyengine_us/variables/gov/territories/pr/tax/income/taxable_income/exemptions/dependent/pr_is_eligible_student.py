from policyengine_us.model_api import *


class pr_is_eligible_student(Variable):
    value_type = bool
    entity = Person
    label = "Puerto Rico dependent exemption eligible student"
    reference = "https://hacienda.pr.gov/sites/default/files/inst_individuals_2023.pdf#page=28"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR

    def formula(person, period, parameters):
        # if dependent is a student, can earn gross income up to 7500 to be eligible for exemption
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.exemptions.dependent
        is_dependent = person("is_tax_unit_dependent", period)
        is_student = person("is_full_time_student", period)
        gross_income = person("pr_gross_income", period)
        income_eligibility = gross_income < p.student_threshold
        return is_dependent & is_student & income_eligibility

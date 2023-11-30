from policyengine_us.model_api import *


class ar_post_secondary_education_tuition_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Arkansas person post-secondary education tuition deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/AR1075_2022.pdf#page=1"
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.ar.tax.income.deductions.itemized.tuition_deduction
        tuition_expenses = person("qualified_tuition_expenses", period)
        technical_institution_student_or_not = person(
            "technical_institution_student", period
        )
        four_year_college_student = person("four_year_college_student", period)

        four_year_student_deduction = min_(
            p.rate * tuition_expenses,
            p.weighted_average_tuition.four_year_college,
        )
        two_year_student_deduction = min_(
            p.rate * tuition_expenses,
            p.weighted_average_tuition.two_year_college,
        )
        technical_institute_student_deduction = min_(
            p.rate * tuition_expenses,
            p.weighted_average_tuition.technical_institutes,
        )

        four_or_two_year_institution_deduction = where(
            four_year_college_student,
            four_year_student_deduction,
            two_year_student_deduction,
        )

        return where(
            technical_institution_student_or_not,
            four_or_two_year_institution_deduction,
            technical_institute_student_deduction,
        )

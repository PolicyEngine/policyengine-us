from policyengine_us.model_api import *


class ar_post_secondary_education_tuition_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas post-secondary education tuition deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/AR1075_2022.pdf#page=1"
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.ar.tax.income.deductions.itemized
        tuition_expense = person("qualified_tuition_expenses", period)
        full_time_college = person("is_full_time_college_student", period)
        four_year_college = person("four_year_college_student", period)

        four_year_deduction = min_(
            p.expense_rate.tuition * tuition_expense,
            p.weighted_average_tuition.four_year_college,
        )
        two_year_deduction = min_(
            p.expense_rate.tuition * tuition_expense,
            p.weighted_average_tuition.two_year_college,
        )
        technical_institute_deduction = min_(
            p.expense_rate.tuition * tuition_expense,
            p.weighted_average_tuition.technical_institutes,
        )

        person_college_deduction = where(
            four_year_college, four_year_deduction, two_year_deduction
        )

        person_tuition_deduction = where(
            full_time_college,
            person_college_deduction,
            technical_institute_deduction,
        )

        return tax_unit.sum(person_tuition_deduction)

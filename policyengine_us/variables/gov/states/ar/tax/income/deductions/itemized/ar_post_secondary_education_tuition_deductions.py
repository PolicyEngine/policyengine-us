from policyengine_us.model_api import *


class ar_post_secondary_education_tuition_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas post-secondary education tuition deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=21"
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.ar.tax.income.deductions.itemized.amount
        tuition_expense = person("qualified_tuition_expenses", period)
        total_tuition_expense = tax_unit.sum(tuition_expense)

        return where(
            person("is_full_time_college_student", period),
            where(
                person("four_year_college_institution", period),
                min(p.ratio * total_tuition_expense, p.four_year_college),
                min(p.ratio * total_tuition_expense, p.two_year_college),
            ),
            min(p.ratio * total_tuition_expense, p.technical_institutes),
        )

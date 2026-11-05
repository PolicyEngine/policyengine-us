from policyengine_us.model_api import *


class ar_post_secondary_education_tuition_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Arkansas person post-secondary education tuition deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/AR1075_2022.pdf#page=1",
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=/ACTS/1997/Public/1075.pdf#page=1",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1075.pdf#page=1",
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.deductions.itemized.tuition
        # Section 26-51-447 and AR1075 leave dependent undefined. Section
        # 26-51-501 limits its IRC 152 definition to personal credits.
        # Retain tuition for a supported student on a claimable return
        # pending resolution of that statutory ambiguity.
        tuition_expenses = person("qualified_tuition_expenses", period)
        uncapped = p.rate * tuition_expenses
        cap = select(
            [
                person("technical_institution_student", period),
                person("four_year_college_student", period),
            ],
            [
                p.weighted_average_tuition.technical_institutes,
                p.weighted_average_tuition.four_year_college,
            ],
            default=p.weighted_average_tuition.two_year_college,
        )
        return min_(uncapped, cap)

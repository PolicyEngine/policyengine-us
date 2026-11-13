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
        "https://codeofarrules.arkansas.gov/Rules/Rule?chapterID=33&levelType=section&partID=941&sectionID=40250&subChapterID=261&subPartID=6195&titleID=26",
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.deductions.itemized.tuition
        # 26-51-447 leaves "dependent" undefined, and 26-51-501(a)(3)(B)
        # applies the IRC 152 definition only within its own subdivision.
        # DFA's definition, 26 CAR 100-143(f), tests relationship, income,
        # support, joint filing and citizenship, and doesn't ask whether
        # another taxpayer can claim the filer. So a claimable filer deducts
        # tuition paid for a student who meets those tests.
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

from policyengine_us.model_api import *


class sc_tuition_credit(Variable):
    value_type = float
    entity = Person
    label = "South Carolina Tuition Credit"
    defined_for = "sc_tuition_credit_eligible"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/forms-site/Forms/I319_2021.pdf#page=2",
        "https://www.scstatehouse.gov/code/t12c006.php"
        # South Carolina Legal Code | SECTION 12-6-3385 (A)
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sc.tax.income.credits.college_tuition

        # line 1
        total_college_hours = person("total_college_hours", period)
        # line 2
        qualified_tuition_expenses = person(
            "qualified_tuition_expenses", period
        )
        # line 3
        sc_tuition_credit_eligible = person(
            "sc_tuition_credit_eligible", period
        )
        tuition_limit = (
            p.max_amount.tuition
            * total_college_hours
            / (p.semester_hour_requirement * p.max_semester_attend)
        ) * sc_tuition_credit_eligible
        # line 7 (lesser of line 2 or 3 and multiply by rate)
        uncapped_credit = (
            min_(qualified_tuition_expenses, tuition_limit) * p.rate
        )
        tuition_credit = min_(uncapped_credit, p.max_amount.credit)
        # compare line 7 with credit max amount, take lesser amount
        return where(sc_tuition_credit_eligible, tuition_credit, 0)

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
        "https://www.scstatehouse.gov/code/t12c006.php",
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
        # line 3,4,7
        tuition_max_amount = p.rate.thresholds[1]
        qualified_tuition_expenses_credit = p.rate.calc(
            qualified_tuition_expenses
        )
        max_hour = p.semester_hour_requirement.calc(total_college_hours)
        tuition_limit_credit = p.rate.calc(
            tuition_max_amount * total_college_hours / (max_hour)
        )

        uncapped_credit = min_(
            qualified_tuition_expenses_credit, tuition_limit_credit
        )

        # compare line 7 with credit max amount, take lesser amount
        return min_(uncapped_credit, p.cap)

from policyengine_us.model_api import *


class ne_refundable_ctc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Nebraska refundable Child Tax Credit eligible child"
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-7202"
    )
    defined_for = StateCode.NE

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.credits.ctc.refundable
        age_eligible = person("age", period) <= p.age_threshold
        is_dependent = person("is_tax_unit_dependent", period)
        age_eligible_dependent = age_eligible & is_dependent
        child_care_enrolled_child = person(
            "ne_ctc_child_enrolled_in_eligible_care_program", period
        )
        child_care_receiving_child = person(
            "ne_ctc_child_receives_child_care", period
        )
        income_eligible = person.tax_unit(
            "ne_refundable_ctc_income_eligible", period
        )
        return age_eligible_dependent & (
            child_care_enrolled_child
            | child_care_receiving_child
            | income_eligible
        )

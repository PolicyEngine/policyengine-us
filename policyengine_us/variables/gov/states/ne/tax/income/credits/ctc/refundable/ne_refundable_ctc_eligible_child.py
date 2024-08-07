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
        qualifying_child = age_eligible & is_dependent
        child_care_enrolled_child = person(
            "ne_refundable_ctc_child_care_enrolled_eligible_child", period
        )
        child_care_receiving_child = person(
            "ne_refundable_ctc_child_care_receiving_eligible_child", period
        )
        income_eligible = person.tax_unit(
            "ne_refundable_ctc_income_eligible", period
        )
        return qualifying_child & (
            child_care_enrolled_child
            | child_care_receiving_child
            | income_eligible
        )

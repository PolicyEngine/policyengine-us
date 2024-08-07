from policyengine_us.model_api import *


class ne_refundable_ctc_child_care_receiving_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Nebraska refundable Child Tax Credit eligible child via receiving care from an approved license-exempt provider enrolled in the child care subsidy program"
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-7203"
    )
    defined_for = StateCode.NE

    def formula(person, period, parameters):
        return person("pre_subsidy_childcare_expenses", period) > 0

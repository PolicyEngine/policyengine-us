from policyengine_us.model_api import *


class ne_refundable_ctc_child_care_enrolled_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Nebraska refundable Child Tax Credit eligible child via enrollment in a child care program licensed pursuant to the Child Care Licensing Act"
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-7203"
    )
    defined_for = StateCode.NE

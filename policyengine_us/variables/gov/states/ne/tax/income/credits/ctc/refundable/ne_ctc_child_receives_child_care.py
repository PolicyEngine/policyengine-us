from policyengine_us.model_api import *


class ne_ctc_child_receives_child_care(Variable):
    value_type = bool
    entity = Person
    label = "Nebraska refundable Child Tax Credit child receiving care from child care subsidy program"
    documentation = "Nebraska refundable Child Tax Credit eligible child via receiving care from an approved license-exempt provider enrolled in the child care subsidy program"
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-7203"
    )
    defined_for = StateCode.NE

    def formula(person, period, parameters):
        return person("pre_subsidy_childcare_expenses", period) > 0

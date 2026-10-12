from policyengine_us.model_api import *


class ne_child_care_subsidy_at_redetermination(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy redetermination status"
    documentation = "This input variable defaults to false, so microsimulation runs evaluate every household under initial-application rules rather than the 200% FPG redetermination income limit."
    defined_for = StateCode.NE
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1206",
        "https://nebraskalegislature.gov/FloorDocs/109/PDF/Slip/LB304.pdf#page=2",
    )

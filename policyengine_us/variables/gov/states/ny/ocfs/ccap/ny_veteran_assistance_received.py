from policyengine_us.model_api import *


class ny_veteran_assistance_received(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Receives New York veteran assistance"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period
    default_value = False
    defined_for = StateCode.NY
    documentation = (
        "Records veteran assistance receipt by a parent or caretaker "
        "relative in the SPM unit during the month. New York includes that program within public "
        "assistance under Social Services Law section 2(19)."
    )
    reference = "https://www.nysenate.gov/legislation/laws/SOS/2"

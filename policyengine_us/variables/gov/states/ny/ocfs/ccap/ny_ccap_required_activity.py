from policyengine_us.model_api import *


class ny_ccap_required_activity(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New York CCAP caretaker participates in a required activity"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period
    default_value = False
    defined_for = StateCode.NY
    documentation = (
        "Records whether the family meets the caretaker conditions through "
        "activities a social services official requires under 18 NYCRR "
        "415.2(a)(1). Officials may require orientation, assessment or work "
        "activities. For two-caretaker families, each caretaker must satisfy "
        "an applicable required-activity or work condition."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=13",
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-415.2",
    )

from policyengine_us.model_api import *


class id_iccp_has_constant_supervision_plan(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Has an order or case plan requiring constant supervision for Idaho ICCP"
    defined_for = StateCode.ID
    documentation = (
        "Whether a court order, probation order, child-protection case plan, or "
        "mental-health case plan requires constant supervision of this child, as "
        "specified in IDAPA 16.06.12.105.03.b. This does not imply disability or "
        "a protective-services waiver."
    )
    reference = "https://files.dfm.idaho.gov/dfm-admin-website/rules/current/16/160612.pdf#page=12"

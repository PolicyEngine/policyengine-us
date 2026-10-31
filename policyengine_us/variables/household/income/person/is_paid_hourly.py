from policyengine_us.model_api import *


class is_paid_hourly(Variable):
    value_type = bool
    entity = Person
    label = "is paid hourly"
    documentation = (
        "Whether the person is paid by the hour, imputed from CPS ORG donors. "
        "The default is false, so a record without it fails hourly-pay tests."
    )
    definition_period = YEAR

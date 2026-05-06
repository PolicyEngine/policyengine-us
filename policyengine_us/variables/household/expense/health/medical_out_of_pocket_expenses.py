from policyengine_us.model_api import *


class medical_out_of_pocket_expenses(Variable):
    value_type = float
    entity = Person
    label = "Medical out-of-pocket expenses (deprecated)"
    unit = USD
    definition_period = YEAR
    documentation = (
        "DEPRECATED. Removed in 1.673.0 and restored as a temporary "
        "alias to ease migration. Values supplied here are forwarded "
        "into `other_medical_expenses`. Migrate to `other_medical_expenses` "
        "for non-premium medical spending and to `health_insurance_premiums` "
        "if your value previously included health insurance premiums. "
        "This alias will be removed in a future release."
    )

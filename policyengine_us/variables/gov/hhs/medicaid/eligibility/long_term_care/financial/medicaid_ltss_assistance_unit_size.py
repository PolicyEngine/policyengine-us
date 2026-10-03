from policyengine_us.model_api import *


class medicaid_ltss_assistance_unit_size(Variable):
    value_type = int
    entity = Person
    label = "Medicaid LTSS assistance unit size"
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Explicit size of the assistance unit used by the Medicaid LTSS "
        "financial threshold screen. It is not inferred from a tax unit, "
        "household, or marital unit. Zero is unsupported and therefore "
        "fail-closed."
    )
    reference = "https://www.law.cornell.edu/cfr/text/42/435.601"

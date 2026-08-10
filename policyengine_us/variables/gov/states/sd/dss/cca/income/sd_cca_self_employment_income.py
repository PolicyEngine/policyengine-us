from policyengine_us.model_api import *


class sd_cca_self_employment_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "South Dakota CCA countable self-employment income"
    definition_period = YEAR
    defined_for = StateCode.SD
    reference = (
        "https://dss.sd.gov/docs/childcare/assistance/Subsidy_Manual.pdf#page=14"
    )

    def formula(person, period, parameters):
        # Subsidy Manual, Section 6: "Self-employment showing a loss shall be
        # counted as $0.00. A loss may not be deducted from other forms of
        # income the household may have." We floor self-employment income at
        # zero per person so a loss cannot offset other income. PolicyEngine
        # carries a single aggregate self-employment figure per person, so the
        # Manual's per-business separation (a loss from one business will not
        # offset another) is not modeled.
        return max_(person("self_employment_income", period), 0)

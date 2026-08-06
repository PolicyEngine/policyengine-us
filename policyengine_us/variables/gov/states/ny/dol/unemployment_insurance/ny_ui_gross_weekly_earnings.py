from policyengine_us.model_api import *


class ny_ui_gross_weekly_earnings(Variable):
    value_type = float
    entity = Person
    label = "New York unemployment insurance gross weekly earnings"
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = "https://www.nysenate.gov/legislation/laws/LAB/590"
    documentation = (
        "Claim-week gross earnings used for the partial-benefit earnings gate "
        "and the $869 earnings cutoff. Per NYSDOL P803, self-employment "
        "earnings are excluded from the earnings cutoff test. The annual "
        "definition period treats the value as a single representative claim "
        "week."
    )
    defined_for = StateCode.NY

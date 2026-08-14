from policyengine_us.model_api import *


class ny_ui_gross_weekly_earnings(Variable):
    value_type = float
    entity = Person
    label = "New York unemployment insurance gross weekly earnings"
    unit = USD
    definition_period = YEAR
    reference = "https://dol.ny.gov/system/files/documents/2025/10/p803-partial-ui-faqs-10-3-25.pdf#page=1"
    documentation = (
        "Claim-week gross earnings used for the partial-benefit earnings gate "
        "and the $869 earnings cutoff. Per NYSDOL P803, self-employment "
        "earnings are excluded from the earnings cutoff test. The annual "
        "definition period treats the value as a single representative claim "
        "week."
    )
    defined_for = StateCode.NY

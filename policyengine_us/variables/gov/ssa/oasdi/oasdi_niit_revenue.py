from policyengine_us.model_api import *


class oasdi_niit_revenue(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "OASDI modeled net investment income tax transfer"
    documentation = (
        "The OASDI transfer selected by the S.770 section 8 options "
        "(s770_revenue_oasdi): zero unless an option applies. This is the "
        "transfer under the selected mode, not the full net investment "
        "income tax liability."
    )
    unit = USD
    reference = "https://www.congress.gov/bill/119th-congress/senate-bill/770/text"
    adds = ["s770_revenue_oasdi"]

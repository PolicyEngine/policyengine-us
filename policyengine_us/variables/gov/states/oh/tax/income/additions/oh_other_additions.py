from policyengine_us.model_api import *


class oh_other_additions(Variable):
    value_type = float
    entity = Person
    label = "Ohio other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH
    documentation = (
        "Ohio other additions reported on Ohio Schedule of Adjustments, "
        "line 10 (Other additions), entered as a positive amount."
    )
    reference = "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=19"

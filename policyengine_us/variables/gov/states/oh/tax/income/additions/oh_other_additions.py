from policyengine_us.model_api import *


class oh_other_additions(Variable):
    value_type = float
    entity = Person
    label = "Ohio other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH
    documentation = (
        "Ohio Schedule of Adjustments additions (lines 1-11) not otherwise modeled, "
        "entered as a positive amount. Do not include the bonus depreciation add-back "
        "on line 9 (oh_bonus_depreciation_add_back), which PolicyEngine computes separately."
    )
    reference = "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=19"

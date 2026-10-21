from policyengine_us.model_api import *


class nc_lieap_nonbank_resources(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    quantity_type = STOCK
    unit = USD
    label = "North Carolina LIEAP cash and lump sums outside bank accounts"
    documentation = (
        "Cash on hand and retained lump-sum payments at application that are "
        "not included in bank_account_assets. Count each amount once: a lump "
        "sum held as cash is part of this total, not an additional amount. "
        "Include resources of ineligible household members."
    )
    reference = (
        # Section 300.11 (pages 17-18); the counted resources are listed on
        # page 18.
        "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=18",
    )

from policyengine_us.model_api import *


class in_bonus_depreciation_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN bonus depreciation add back"
    definition_period = YEAR
    documentation = "Income (or loss) included in Federal AGI under Section 168(k)'s bonus depreciation less the amount that would have been included without it."
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"  # (a)(15)
    # use federal variables if they are added later

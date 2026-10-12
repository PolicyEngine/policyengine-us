from policyengine_us.model_api import *


class farm_rent_income(Variable):
    value_type = float
    entity = Person
    label = "farm rental income"
    documentation = (
        "Net farm rental income or loss from Form 4835: crop or livestock "
        "shares a landowner (or sub-lessor) receives from a farm in which "
        "they do not materially participate. It is reported on Schedule E "
        "line 40 and is not subject to self-employment tax."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1402",
        "https://www.irs.gov/pub/irs-prior/f4835--2025.pdf#page=2",
    )
    uprating = "calibration.gov.irs.soi.farm_rent_income"

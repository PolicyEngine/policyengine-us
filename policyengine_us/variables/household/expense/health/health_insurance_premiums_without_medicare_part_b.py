from policyengine_us.model_api import *


class health_insurance_premiums_without_medicare_part_b(Variable):
    value_type = float
    entity = Person
    label = "Health insurance premiums without Medicare Part B premiums"
    unit = USD
    definition_period = YEAR
    # Survey data carry the person's reported premiums here (CPS ASEC
    # PHIP_VAL), most of them paid by people with employer-sponsored
    # coverage. They follow the same premium index as
    # pre_tax_health_insurance_premiums, so a premium moved from one input
    # to the other grows the same way.
    uprating = "calibration.gov.hhs.cms.esi_premium_per_enrollee"

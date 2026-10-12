from policyengine_us.model_api import *


class employer_sponsored_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Employer-sponsored insurance premiums"
    documentation = (
        "Annual employer-paid health insurance premiums. CBO treats this "
        "as part of household market income. Uprated by CMS's "
        "employer-sponsored insurance premium per enrollee, so each "
        "policyholder's premium grows with premiums rather than wages. This "
        "is a premium-growth proxy: it holds the number of people covered "
        "per policy and the employer's share of the premium, which CMS "
        "projects as roughly constant, at their base-year levels. The number "
        "of policyholders follows the weights."
    )
    definition_period = YEAR
    unit = USD
    uprating = "calibration.gov.hhs.cms.esi_premium_per_enrollee"

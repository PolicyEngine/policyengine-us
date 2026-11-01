from policyengine_us.model_api import *


class s770_revenue_oasdi(Variable):
    value_type = float
    entity = TaxUnit
    label = "OASDI revenue from S.770 section 8 options"
    documentation = "Sum each TaxUnit once, alongside tob_revenue_oasdi; includes the existing NIIT transfer only where the selected mode transfers it. Liability and trust-fund allocation equivalence are separate claims."
    unit = USD
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/senate-bill/770/text"
    adds = [
        "s770_existing_niit_revenue_oasdi",
        "s770_nii_addon_revenue_oasdi",
        "s770_active_business_income_revenue_oasdi",
    ]

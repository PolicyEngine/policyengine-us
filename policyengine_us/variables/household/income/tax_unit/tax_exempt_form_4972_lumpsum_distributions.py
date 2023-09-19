from policyengine_us.model_api import *


class tax_exempt_form_4972_lumpsum_distributions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Lump-sum distributions reported on IRS Form 4972 not included in federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    documentation = "Lump-sum distributions reported on IRS Form 4972 not included in federal adjusted gross income."

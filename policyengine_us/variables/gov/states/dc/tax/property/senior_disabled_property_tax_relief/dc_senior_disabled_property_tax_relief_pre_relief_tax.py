from policyengine_us.model_api import *


class dc_senior_disabled_property_tax_relief_pre_relief_tax(Variable):
    """Explicit applicable tax base before the senior/disabled bill reduction.

    Enter tax after applicable homestead and assessment relief, but before this
    reduction, on the eligible residence or attributable cooperative dwelling.
    Include only the approved installment coverage; do not infer a full year from
    end-of-year age or eligibility. Assign the complete base once, to one TaxUnit
    containing a qualifying owner; all other TaxUnits in the home enter zero.
    The model cannot detect duplicated parcel bills across TaxUnits. Do not copy
    an already-reduced bill here or infer this amount from real_estate_taxes.
    Schedule H continues to use its separate actual net tax-bill input. Unknown
    base or installment facts leave this input zero and suppress the estimate.
    """

    value_type = float
    entity = TaxUnit
    label = "DC senior disabled property tax relief applicable pre-relief tax"
    unit = USD
    definition_period = YEAR
    default_value = 0
    reference = "https://code.dccouncil.gov/us/dc/council/code/sections/47-863"

# Disposable income of cotenants who occupy the residence but file
# outside this tax unit. Per RCW 84.36.383(2), combined disposable
# income includes each cotenant's disposable income. Default is zero;
# populate when the household has occupying co-owners filing separate
# federal returns.
from policyengine_us.model_api import *


class wa_pte_cotenant_disposable_income(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    definition_period = YEAR
    label = "Washington Senior/Disabled PTE cotenant disposable income"
    defined_for = StateCode.WA
    reference = ("https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.383",)

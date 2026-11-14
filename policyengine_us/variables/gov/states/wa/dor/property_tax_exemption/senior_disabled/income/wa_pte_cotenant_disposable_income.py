# Disposable income of cotenants (residents with an ownership interest in
# the residence, RCW 84.36.383(3)) other than the tax unit head and spouse:
# co-owners who file their own federal returns, and a tax unit dependent
# who owns part of the residence. Per RCW 84.36.383(2), combined
# disposable income includes each cotenant's disposable income. Default is
# zero.
from policyengine_us.model_api import *


class wa_pte_cotenant_disposable_income(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    definition_period = YEAR
    label = "Washington Senior/Disabled PTE cotenant disposable income"
    defined_for = StateCode.WA
    reference = ("https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.383",)

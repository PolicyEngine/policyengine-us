## md_pass_through_member_share_addition.py
from openfisca_us.model_api import *

class md_pass_through_member_share_addition(Variable):
    # r. Members of pass-through entities that elected to make payments attributable to members’ share of the pass-through entity taxable income. If you received a credit for tax paid by the pass-through entity on your distributive or pro rata share of income on Maryland Schedule K-1 (510), part D enter the amount of the credit claimed on Form 502CR part CC line 9.
    value_type = float
    entity = TaxUnit
    label = "MD pass-through member share"
    documentation = "Members of pass-through entities that elected to make payments attributable to members’ share of the pass-through entity taxable income. If you received a credit for tax paid by the pass-through entity on your distributive or pro rata share of income on Maryland Schedule K-1 (510), part D enter the amount of the credit claimed on Form 502CR part CC line 9."
    unit = USD
    definition_period = YEAR
from policyengine_us.model_api import *


class is_nonresident_alien_for_lifetime_learning_credit(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Nonresident alien for Lifetime Learning Credit"
    documentation = "Whether the taxpayer is a nonresident alien for Lifetime Learning Credit purposes and is not treated as a resident alien under section 6013(g) or 6013(h)."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#g_7"

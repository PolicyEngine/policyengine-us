from policyengine_us.model_api import *


class unadjusted_basis_qualified_property(Variable):
    value_type = float
    entity = Person
    label = "Unadjusted basis for qualified property"
    unit = USD
    documentation = "Share of unadjusted basis upon acquisition of all property held by qualified pass-through businesses."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#b_6"

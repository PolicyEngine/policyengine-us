from policyengine_us.model_api import *


class mt_ssp_receives_section_1619_benefits(Variable):
    value_type = bool
    entity = Person
    label = "Receives section 1619 benefits excluded from Montana supplementation"
    definition_period = MONTH
    default_value = False
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0501415010DEN"
    documentation = "Section 1619(a) receipt, or section 1619 receipt while institutionalized throughout the month, as defined in SI DEN01415.010 B.1."

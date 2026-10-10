from policyengine_us.model_api import *


class ssi_resource_deeming_child_is_ineligible(Variable):
    value_type = bool
    entity = Person
    label = "Child is otherwise ineligible for SSI resource deeming allocation"
    definition_period = MONTH
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0501330200"
    documentation = """
    Adjudicated SSI ineligibility for a reason other than the resource test,
    used to remove a child from the equal parental resource allocation.
    POMS SI 01330.200 B: 'If an eligible child is later determined ineligible
    for any reason' redivide among the remaining eligible children effective
    the first month of ineligibility. Resource ineligibility is calculated
    within the resource deeming formula, avoiding an eligibility cycle.
    """

from policyengine_us.model_api import *


class nh_ssp_grant_reduction_applies(Variable):
    value_type = bool
    entity = Person
    label = "New Hampshire SSP one-third grant reduction applies"
    definition_period = MONTH
    default_value = False
    reference = "https://gc.nh.gov/rules/state_agencies/he-w600.html"
    documentation = """
    State determination under He-W 670.03(c): the independent-living recipient
    lives with others, has no food or residence expenses and receives no SNAP,
    or fails the required documentation. This is a separate determination from
    the federal SSI household reduction. It is explicit to avoid a cycle with
    SNAP, which counts the state grant as income.
    """

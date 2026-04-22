from policyengine_us.model_api import *


class al_ssp_grandfathered(Variable):
    value_type = bool
    entity = Person
    label = "Alabama SSP grandfathered eligibility override"
    definition_period = MONTH
    defined_for = StateCode.AL
    default_value = False
    reference = (
        "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=9",
        "https://admincode.legislature.state.al.us/api/rule/660-2-4-.26",
    )
    documentation = """
    Flags people who remain eligible for Alabama supplementation through the
    grandfathered non-SSI or closed-cohort rules. This is required for
    arrangements such as the cerebral palsy treatment center that are no
    longer broadly open to new recipients.
    """

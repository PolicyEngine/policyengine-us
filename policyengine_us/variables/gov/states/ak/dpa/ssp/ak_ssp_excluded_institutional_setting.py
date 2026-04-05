from policyengine_us.model_api import *


class ak_ssp_excluded_institutional_setting(Variable):
    value_type = bool
    entity = Household
    label = "Alaska APA excluded institutional setting"
    definition_period = YEAR
    defined_for = StateCode.AK
    default_value = False
    reference = (
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ak.pdf#page=1"
    )
    documentation = """
    Flags households in Alaska Pioneer Homes, nonmedical public institutions,
    or institutions for mental disorders. Those settings are explicitly
    excluded from Alaska APA coverage.
    """

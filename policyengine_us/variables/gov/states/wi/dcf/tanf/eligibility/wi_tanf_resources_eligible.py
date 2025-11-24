from policyengine_us.model_api import *


class wi_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wisconsin TANF resources eligible"
    definition_period = YEAR
    reference = (
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/03/"
        "03.3.4_COUNTING_ASSETS.htm",
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/145"
        "#(2)(d)",
    )
    defined_for = StateCode.WI
    documentation = """
    Wisconsin W-2 requires assets (combined equity value) to be less
    than or equal to $2,500, after applying exclusions.
    """

    def formula(spm_unit, period, parameters):
        countable_resources = spm_unit("wi_tanf_countable_resources", period)
        p = parameters(period).gov.states.wi.dcf.tanf.asset_limit
        resource_limit = p.amount
        return countable_resources <= resource_limit

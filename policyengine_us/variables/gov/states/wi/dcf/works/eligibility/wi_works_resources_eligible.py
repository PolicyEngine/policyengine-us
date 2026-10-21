from policyengine_us.model_api import *


class wi_works_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wisconsin Works resources eligible"
    definition_period = YEAR
    reference = (
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/03/03.3.4_COUNTING_ASSETS.htm",
        "https://docs.legis.wisconsin.gov/code/register/2021/790b/insert/dcf101.pdf#page=5",
    )
    defined_for = StateCode.WI

    def formula(spm_unit, period, parameters):
        countable = spm_unit("wi_works_countable_resources", period)
        p = parameters(period).gov.states.wi.dcf.works.asset
        return countable <= p.limit

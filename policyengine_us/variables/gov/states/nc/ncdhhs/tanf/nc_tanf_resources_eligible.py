from policyengine_us.model_api import *


class nc_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "North Carolina TANF resources eligible"
    definition_period = YEAR
    reference = (
        "https://regulations.justia.com/states/north-carolina/title-10a/chapter-71/subchapter-w/section-0400/section-71w-0407",
        "https://policies.ncdhhs.gov/wp-content/uploads/wf115.pdf#page=1",
    )
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.tanf.resources
        countable_resources = spm_unit("nc_tanf_countable_resources", period)
        return countable_resources <= p.limit

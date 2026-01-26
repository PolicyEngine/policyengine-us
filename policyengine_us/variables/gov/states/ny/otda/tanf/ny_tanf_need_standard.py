from policyengine_us.model_api import *


class ny_tanf_need_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York TANF need standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-352.1"
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("spm_unit_size", period.this_year)
        p = parameters(period).gov.states.ny.otda.tanf.need_standard
        capped_size = min_(size, p.max_table_size)
        additional_size = size - capped_size
        return p.main[capped_size] + p.additional * additional_size

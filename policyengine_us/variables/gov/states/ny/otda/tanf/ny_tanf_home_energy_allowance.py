from policyengine_us.model_api import *


class ny_tanf_home_energy_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York TANF home energy allowance"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-352.2"

    def formula(spm_unit, period, parameters):
        size = spm_unit("spm_unit_size", period.this_year)
        p = parameters(period).gov.states.ny.otda.tanf.need_standard
        max_size = p.max_table_size
        capped_size = min_(size, max_size)
        additional_size = size - capped_size
        return (
            p.home_energy.main[capped_size]
            + p.home_energy.additional * additional_size
        )

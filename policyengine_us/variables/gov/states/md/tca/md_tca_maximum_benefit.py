from policyengine_us.model_api import *


class md_tca_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TCA maximum benefit"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.17.aspx"

    def formula(spm_unit, period, parameters):
        size = spm_unit("spm_unit_size", period.this_year)
        p = parameters(period).gov.states.md.tca.maximum_benefit
        capped_size = min_(size, p.max_table_size)
        additional_size = size - capped_size
        base = p.main[capped_size]
        return base + p.additional * additional_size

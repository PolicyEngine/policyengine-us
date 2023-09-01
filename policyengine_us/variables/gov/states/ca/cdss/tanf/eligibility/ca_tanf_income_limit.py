from policyengine_us.model_api import *


class ca_tanf_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Minimum Basic Standard of Adequate Care"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        ceiling = min_(unit_size, 10)
        extra = unit_size - ceiling

        county = spm_unit.household("county_str", period)
        p = parameters(period).gov.states.ca.cdss.tanf.income.limit
        region1 = parameters(period).gov.states.ca.cdss.tanf.region1

        main = where(
            county in region1, 
            p.region1.main[ceiling], 
            p.region2.main[ceiling])
        additional = where(
            county in region1, 
            p.region1.additional, 
            p.region2.additional)

        monthly = main + additional * extra
        return monthly * MONTHS_IN_YEAR
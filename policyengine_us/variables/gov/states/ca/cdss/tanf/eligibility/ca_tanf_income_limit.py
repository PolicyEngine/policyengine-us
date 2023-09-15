from policyengine_us.model_api import *


class ca_tanf_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Minimum Basic Standard of Adequate Care"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.tanf.income.monthly_limit
        unit_size = spm_unit("spm_unit_size", period)
        au_size = min_(unit_size, p.max_au_size)
        additional_people = unit_size - au_size
        region1 = spm_unit("ca_tanf_region1", period)


        main = where(region1, p.region1.main[au_size], p.region2.main[au_size])
        additional = where(region1, p.region1.additional, p.region2.additional)

        monthly_limit = main + additional * additional_people
        return monthly_limit * MONTHS_IN_YEAR

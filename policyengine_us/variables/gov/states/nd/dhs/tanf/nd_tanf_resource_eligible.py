from policyengine_us.model_api import *


class nd_tanf_resource_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for North Dakota TANF due to resources"
    definition_period = MONTH
    reference = (
        "https://www.nd.gov/dhs/policymanuals/40019/400_19_55_05_10.htm"
    )
    defined_for = StateCode.ND

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nd.dhs.tanf.resources.limit
        resources = spm_unit("spm_unit_assets", period.this_year)
        unit_size = spm_unit("spm_unit_size", period.this_year)

        # Resource limits: $3,000 for 1 person, $6,000 for 2+,
        # plus $25 for each additional person beyond 2
        limit = where(
            unit_size == 1,
            p.one_person,
            p.two_persons + max_(unit_size - 2, 0) * p.per_additional_person,
        )
        return resources <= limit

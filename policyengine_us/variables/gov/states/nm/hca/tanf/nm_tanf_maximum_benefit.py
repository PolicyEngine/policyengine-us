from policyengine_us.model_api import *


class nm_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico TANF maximum benefit (payment standard)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.srca.nm.gov/parts/title08/08.102.0500.html",
        "https://www.hca.nm.gov/2023/09/01/state-announces-a-23-percent-increase-in-cash-assistance-for-low-income-new-mexico-families/",
    )
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nm.hca.tanf.payment_standard
        unit_size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(unit_size, p.max_unit_size)
        return p.amount[capped_size]

from policyengine_us.model_api import *


class nm_works_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico Works maximum benefit (payment standard)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.srca.nm.gov/parts/title08/08.102.0500.html",
        "https://www.hca.nm.gov/2023/09/01/state-announces-a-23-percent-increase-in-cash-assistance-for-low-income-new-mexico-families/",
    )
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nm.hca.nm_works.payment_standard
        unit_size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(unit_size, p.max_table_size)
        base_amount = p.amount[capped_size]
        extra_persons = max_(unit_size - p.max_table_size, 0)
        return base_amount + extra_persons * p.additional_person

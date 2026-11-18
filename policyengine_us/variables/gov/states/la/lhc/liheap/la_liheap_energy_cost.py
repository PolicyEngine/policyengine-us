from policyengine_us.model_api import *


class la_liheap_energy_cost(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Louisiana LIHEAP total energy cost"
    documentation = (
        "Annual residential energy bills from all vendors, less the HUD utility "
        "allowance for subsidized households without a counted elderly member. "
        "Negative when the allowance exceeds the bills."
    )
    defined_for = StateCode.LA
    reference = (
        # PDF pages 37-40
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20REVISED%20January%201_%202024.pdf#page=37",
        "https://liheapch.acf.gov/docs/2026/state-plans/LA_Plan_2026.pdf#page=9",
        # PDF pages 43-47
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20FINAL%20-%20Effective%20April%201%2c%202026.pdf#page=43",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.lhc.liheap
        bills = add(spm_unit, period, p.payment.energy_cost_sources)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        person = spm_unit.members
        elderly = spm_unit.any(
            person("is_citizen_or_legal_immigrant", period)
            & (person("age", period) >= p.elderly_age)
        )
        # Total energy cost = vendor energy costs - utility allowance. The
        # shared hud_utility_allowance has no Louisiana schedule, so the
        # allowance is zero unless supplied. A supplied allowance should cover
        # only the heating and cooling utilities (April 2026 guide, Section
        # 4.1 C.1), not water, sewer or trash.
        allowance = spm_unit.household("hud_utility_allowance", period)
        return where(subsidized & ~elderly, bills - allowance, bills)

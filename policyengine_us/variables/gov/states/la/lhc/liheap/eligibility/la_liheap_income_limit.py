from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit


class la_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Louisiana LIHEAP income limit"
    defined_for = StateCode.LA
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/LA_Plan_2026.pdf#page=9",
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Notice%20LHP-2025-01%20-%20LIHEAP%20Income%20Eligibility%20Limits%20for%20FFY2026%20-%20LOUISIANA.pdf",
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20REVISED%20January%201_%202024.pdf#page=29",
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20FINAL%20-%20Effective%20April%201%2c%202026.pdf#page=34",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.lhc.liheap.eligibility
        size = spm_unit("la_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        # The HHS floor order reproduces all ten FFY2026 notice rows. Sizes above
        # 10 follow the federal size factors without a published Louisiana row.
        limit = liheap_smi_limit(size, state, p.smi_rate, period, parameters)
        return where(size > 0, limit, 0)

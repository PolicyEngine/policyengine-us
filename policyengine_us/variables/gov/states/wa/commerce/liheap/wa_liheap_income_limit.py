from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class wa_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Washington LIHEAP annual income limit"
    documentation = (
        "Uses the exact annual federal poverty guideline at season start. "
        "Provider monthly displays differ in rounding; they are not multiplied "
        "back to annual income. This is a documented modeling convention."
    )
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/WA_Plan_2026.pdf#page=8",
        "https://drive.google.com/file/d/18fvR5CL8UKpTj4Vsm7KlkitKUJclAvkR/view#page=1",
        "https://deptofcommerce.app.box.com/s/3fp0xz4y2x2p4hedw9ww4sk7ma36srlx",
    )
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wa.commerce.liheap
        size = spm_unit("wa_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            max_(size, 1), state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        return where(size > 0, guideline * p.fpg_rate, 0)

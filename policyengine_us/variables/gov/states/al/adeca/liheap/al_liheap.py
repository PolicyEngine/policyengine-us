from policyengine_us.model_api import *


class al_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Alabama LIHEAP regular heating assistance"
    defined_for = StateCode.AL
    # Manual pages 22-23 cover the HUD adjustment and discretionary high need.
    reference = (
        "https://adeca.alabama.gov/wp-content/uploads/FY-2026-LIHEAP-Manual-1.pdf#page=22",
        "https://adeca.alabama.gov/wp-content/uploads/FY-2026-LIHEAP-State-Plan.pdf#page=10",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.adeca.liheap.payment
        eligible = spm_unit("al_liheap_eligible", period)
        base = spm_unit("al_liheap_base_payment", period)
        # The monthly HUD allowance reduces the award, not countable income.
        # AL local allowance schedules are not encoded in the shared input;
        # an observed annual allowance can be supplied directly.
        allowance = spm_unit.household("hud_utility_allowance", period) / MONTHS_IN_YEAR
        regular_payment = max_(base - allowance, 0)
        # FY2026 IIJA funds were awarded; assume program funds are available.
        # Interpret the plan's "receives a Heating benefit" as requiring a
        # positive regular payment after the HUD adjustment. The plan does
        # not expressly address a regular payment reduced to zero.
        supplement = where(regular_payment > 0, p.iija_supplement, 0)
        # The separate $50 high-need addition requires an agency decision
        # unavailable in existing inputs, so demographic traits alone do not
        # add it. FY2027 supplement policy is not verified by the draft plan.
        # Fixed regular payments have no cap at the reported heating expense.
        return eligible * (regular_payment + supplement)

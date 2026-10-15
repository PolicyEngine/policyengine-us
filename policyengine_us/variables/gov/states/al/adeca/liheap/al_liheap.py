from policyengine_us.model_api import *


class al_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Alabama LIHEAP regular heating assistance"
    defined_for = StateCode.AL
    reference = (
        # PDF pages 22-23
        "https://adeca.alabama.gov/wp-content/uploads/FY-2026-LIHEAP-Manual-1.pdf#page=22",
        "https://liheapch.acf.gov/docs/2026/state-plans/AL_Plan_2026.pdf#page=10",
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
        # The plan pays the $100 IIJA supplement "if funding is available".
        # The FY2026 award (2601ALLIEI, $1,359,705, roughly 13,600 supplements
        # across heating and cooling) can run out during the season; the model
        # assumes it does not, so population totals overstate funded awards.
        # The draft FY2027 plan drops the supplement, which ends after FY2026.
        # Interpret the plan's "receives a Heating benefit" as requiring a
        # positive regular payment after the HUD adjustment. The plan does
        # not expressly address a regular payment reduced to zero.
        supplement = where(regular_payment > 0, p.iija_supplement, 0)
        # The separate $50 high-need addition requires an agency decision
        # unavailable in existing inputs, so demographic traits alone do not
        # add it. Fixed regular payments have no cap at the reported heating
        # expense.
        return eligible * (regular_payment + supplement)

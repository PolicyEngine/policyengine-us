from policyengine_us.model_api import *


class ct_ceap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut Energy Assistance Program regular heating benefit"
    unit = USD
    definition_period = YEAR
    defined_for = "ct_ceap_eligible"
    # PDF pages 6,10-11,15
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/winter-heating-assistance/09012026/ffy-27-liheap-allocation-plan.pdf#page=6"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.ceap.payment
        # State-scoped helpers return zero on other-state rows in a mixed
        # simulation. Keep all vectorized lookups valid before eligibility masks.
        level = max_(spm_unit("ct_ceap_benefit_level", period), 1)
        person = spm_unit.members
        age = person("age", period)
        qualified = person("is_citizen_or_legal_immigrant", period)
        qualified = qualified & ~person("is_in_foster_care", period.first_month)
        vulnerable = spm_unit.any(
            qualified
            & (
                (age >= p.vulnerable.elderly_age)
                | (age < p.vulnerable.young_child_age)
                | person("is_disabled", period)
            )
        )
        basic = p.basic[level] + vulnerable * p.vulnerable.supplement
        # Utility credits exceeding covered-season charges must be returned;
        # delivered-fuel payments cover actual deliveries. Annual primary-fuel
        # expense approximates covered-season cost and oil vendor pricing.
        direct_payment = min_(basic, max_(spm_unit("heating_expense", period), 0))
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        # Rental cash grants have no bill cap. Prior awards/moves, the separate
        # SNAP nominal payment, crisis, weatherization and equipment are excluded.
        return where(heat_in_rent, p.rental[level], direct_payment)

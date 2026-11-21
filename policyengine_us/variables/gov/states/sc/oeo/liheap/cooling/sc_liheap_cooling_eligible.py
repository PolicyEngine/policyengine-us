from policyengine_us.model_api import *


class sc_liheap_cooling_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for South Carolina LIHEAP regular cooling assistance"
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        # PDF pages 4,10
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20LIHEAP%20State%20Plan.pdf#page=4",
        # PDF pages 4,10
        "https://liheapch.acf.gov/docs/2027/state-plans/SC_Plan_2027.pdf#page=4",
        # PDF pages 523,536-537
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20South%20Carolina%20LIHEAP%20Model%20Plan%20w%20Attachments.pdf#page=523",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.oeo.liheap.payment
        income_eligible = spm_unit("sc_liheap_income_eligible", period)
        # Plan items 3.1-3.6 set the cooling income threshold and supplements
        # with no heating-fuel condition, so a household that reports no
        # heating fuel can still receive cooling. The obligation to pay a home
        # energy bill (OEO's 2024 guide) is shown as for heating: any counted
        # energy bill, or heat in the rent, since item 3.3 sets no differing
        # policy for renters with utilities in the rent.
        has_energy_cost = add(spm_unit, period, p.energy_cost_sources) > 0
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        # OEO's texts set no separate cooling-cost test; requiring
        # has_cooling_expense is a PolicyEngine convention.
        has_cooling_expense = spm_unit("has_cooling_expense", period)
        return income_eligible & has_cooling_expense & (has_energy_cost | heat_in_rent)

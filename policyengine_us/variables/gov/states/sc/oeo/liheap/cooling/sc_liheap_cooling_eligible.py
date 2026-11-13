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
        # Cooling-season Direct Assistance uses the regular income and
        # energy-bill tests, which pay an unspecified heating fuel only with
        # heat in the rent; the cooling gate adds no heating-fuel condition.
        # OEO's texts set no separate cooling-cost test; requiring
        # has_cooling_expense is a PolicyEngine convention.
        eligible = spm_unit("sc_liheap_eligible", period)
        return eligible & spm_unit("has_cooling_expense", period)

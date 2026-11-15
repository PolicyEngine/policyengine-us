from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.sc.oeo.liheap.sc_liheap import (
    sc_liheap_award,
)


class sc_liheap_cooling(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina LIHEAP regular cooling assistance"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Cooling-season (May 1 to September 30) nonemergency Direct Assistance "
        "award; when a program year allows one award (FY2027), only its excess "
        "over the heating award. Verified for FY2026 and FY2027; earlier years "
        "use model parameter backfilling and are unverified historical "
        "estimates."
    )
    defined_for = "sc_liheap_cooling_eligible"
    reference = (
        # PDF pages 4,10-11,26
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20LIHEAP%20State%20Plan.pdf#page=4",
        # PDF pages 4,10-11,26
        "https://liheapch.acf.gov/docs/2027/state-plans/SC_Plan_2027.pdf#page=4",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/SC_BenefitMatrix_2026.pdf#page=1",
        # PDF pages 523,536,538
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20South%20Carolina%20LIHEAP%20Model%20Plan%20w%20Attachments.pdf#page=523",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.oeo.liheap
        # The cooling season pays the base and household supplements, with no
        # fuel supplement, up to the cooling maximum.
        award = sc_liheap_award(spm_unit, period, parameters, p.cooling.amounts, 0)
        # FY2026 plan item 11.5 allows two LIHEAP services in the program year,
        # so the cooling award is paid alongside the heating award. FY2027 plan
        # items 1.1 and 11.5 allow one assistance in the 2027 program year, the
        # calendar year that holds both seasons, so cooling pays only its excess
        # over the heating award and the household receives the larger of the
        # two. The 2027 heating amounts are FY2026 carry-forwards.
        if p.payment.max_awards > 1:
            return award
        heating = spm_unit("sc_liheap", period)
        return max_(award - heating, 0)

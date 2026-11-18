from policyengine_us.model_api import *


class de_liheap_cooling_max(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Delaware LIHEAP summer cooling estimated maximum benefit"
    documentation = (
        "The maximum estimated cooling benefit that the Delaware LIHEAP State Plan "
        "prints in section 3.6, for households eligible for the Summer Cooling "
        "Assistance Program electric benefit. This is a published cap, not a computed "
        "award: the State divides the funds available for the electric benefit "
        "equally among eligible households, so the actual amount is not known in "
        "advance. The plan prints one range for the whole cooling component, which "
        "includes the electric benefit and air conditioners, and does not split it. "
        "It is not a payment and is not counted in liheap."
    )
    defined_for = "de_liheap_cooling_eligible"
    reference = (
        # Section 3.6, PDF page 13
        "https://liheapch.acf.gov/docs/2026/state-plans/DE_Plan_2026.pdf#page=13",
        # Section 3.6, PDF page 12
        "https://liheapch.acf.gov/docs/2027/state-plans/DE_Plan_2027.pdf#page=12",
    )

    def formula(spm_unit, period, parameters):
        # A cap, not a payment, so it is not listed in
        # gov.hhs.liheap.regular_payments and does not enter benefit totals.
        return parameters(period).gov.states.de.dhss.liheap.cooling.benefit.maximum

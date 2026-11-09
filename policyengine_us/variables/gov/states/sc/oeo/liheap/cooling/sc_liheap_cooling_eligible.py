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
        # energy-bill tests, and pays only households with cooling costs.
        # heating_type is a required input; an unspecified fuel pays nothing,
        # even with heat included in the rent. Homes without heating (NONE)
        # and every known fuel can qualify.
        fuel = spm_unit("heating_type", period)
        known_fuel = fuel != fuel.possible_values.UNSPECIFIED
        return (
            spm_unit("sc_liheap_eligible", period)
            & spm_unit("has_cooling_expense", period)
            & known_fuel
        )

from policyengine_us.model_api import *


class va_eap_points(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Virginia EAP benefit points"
    documentation = (
        "Total benefit matrix points: household size, income, climate zone, "
        "vulnerability, living arrangement, primary fuel and energy burden. The "
        "primary fuel (10) and energy burden (13) points are PolicyEngine "
        "placeholders applied to every household, because VDSS sets them each "
        "year from an unpublished vendor fuel survey."
    )
    reference = (
        # PDF pages 6-7
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/VA_BenefitMatrix_2026.pdf#page=6",
        # PDF pages 52-53, 65-66
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/eap/Complete_Manual.pdf#page=52",
        "https://liheapch.acf.gov/docs/2026/state-plans/VA_Plan_2026.pdf#page=9",
        "https://law.lis.virginia.gov/admincodefull/title22/agency40/chapter680/",
    )
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.eap.points
        size = spm_unit("va_eap_household_size", period)
        zone = spm_unit("va_eap_climate_zone", period)
        # Every eligible living arrangement code (A, C, E, G, P) scores the
        # same, so the living arrangement points apply to every household.
        return (
            p.household_size.calc(size)
            + spm_unit("va_eap_income_points", period)
            + p.climate_zone[zone]
            + spm_unit("va_eap_vulnerability_points", period)
            + p.living_arrangement
            + p.primary_fuel
            + p.energy_burden
        )

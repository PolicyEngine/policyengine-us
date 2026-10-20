from policyengine_us.model_api import *


class va_eap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Virginia EAP fuel assistance"
    documentation = (
        "Virginia household with at least one citizen or qualified alien member "
        "that is income eligible, heats with electricity, natural gas, oil, "
        "kerosene, propane, wood or coal, and pays for heat directly or through "
        "rent. Subsidized households whose heat is included in rent and homeless "
        "households are ineligible. heating_type is a required input: an "
        "unspecified fuel is ineligible, including when heat is included in "
        "rent. Licensed facilities, group homes, one-room occupants and the "
        "excess-usage-only subsidized arrangement have no inputs and are not "
        "modeled. There is no asset test."
    )
    reference = (
        # PDF pages 25-27, 31, 50
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/eap/Complete_Manual.pdf#page=25",
        "https://liheapch.acf.gov/docs/2026/state-plans/VA_Plan_2026.pdf#page=8",
        "https://law.lis.virginia.gov/admincodefull/title22/agency40/chapter680/",
        # PDF pages 1-2
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/403-errors/FUEL-ASSISTANCE-APPLICATION.pdf#page=1",
    )
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.eap.eligibility
        # Manual B.7: household members must be citizens or qualified aliens.
        has_eligible_member = spm_unit("va_eap_household_size", period) > 0
        income_eligible = spm_unit("va_eap_income_eligible", period)
        # Manual B.5.c.1.a: "The primary fuel will be one of the following:
        # electricity, oil, kerosene, natural gas, LP gas, wood, or coal."
        heating_type = spm_unit("heating_type", period)
        eligible_fuel = np.isin(heating_type.decode_to_str(), p.heating_types)
        # Manual D.1.c: a heating expense is incurred directly (billed) or
        # indirectly, "such as: an undesignated portion of the rent"; B.5.c.1.b
        # admits households whose total heating expenses are included in their
        # rent, "except for those in subsidized housing".
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        pays_for_heat = spm_unit("has_heating_expense", period) | heat_in_rent
        # Manual B.5.c.2.a: "Subsidized households whose total heating costs
        # are included in their rent" are ineligible; subsidized households
        # paying their own heating bills remain eligible (B.5.c.1.c, code G).
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        # Manual B.5.c.2.f-g: persons with no physical address or who are
        # homeless are ineligible.
        homeless = spm_unit.household("is_homeless", period)
        return (
            has_eligible_member
            & income_eligible
            & eligible_fuel
            & pays_for_heat
            & ~(heat_in_rent & subsidized)
            & ~homeless
        )

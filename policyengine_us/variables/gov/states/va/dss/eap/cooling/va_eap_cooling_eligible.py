from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.va.dss.eap.va_eap_income_eligible import (
    va_eap_income_test,
)


class va_eap_cooling_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Virginia EAP cooling assistance electric bill payment"
    reference = (
        # PDF pages 120-122, 127-128
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/eap/Complete_Manual.pdf#page=120",
        # PDF pages 11-12
        "https://liheapch.acf.gov/docs/2026/state-plans/VA_Plan_2026.pdf#page=11",
        "https://law.lis.virginia.gov/admincode/title22/agency40/chapter680/section63/",
        "https://law.lis.virginia.gov/admincode/title22/agency40/chapter680/section10/",
    )
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        # Manual J.3.a applies the Chapter B.6-8 income and citizenship
        # criteria; no heating fuel is required. heating_type is a required
        # input: NONE and every known fuel qualify, UNSPECIFIED does not.
        heating_type = spm_unit("heating_type", period)
        heating_type_reported = heating_type != heating_type.possible_values.UNSPECIFIED
        has_eligible_member = spm_unit("va_eap_household_size", period) > 0
        limit = spm_unit("va_eap_cooling_income_limit", period)
        income_eligible = va_eap_income_test(spm_unit, period, limit)
        # Manual J.3.c: "at least one vulnerable person (a person who is age
        # 60 or older, under age 6 or disabled)". Each of these conditions
        # scores positive vulnerability points.
        vulnerable = spm_unit("va_eap_vulnerability_points", period) > 0
        # Manual J.3.f.1: households without a regular cooling expense
        # (living arrangements B and F) receive equipment only. Plan 3.3:
        # subsidized households whose cooling is in rent are not eligible.
        has_cooling_expense = spm_unit("has_cooling_expense", period)
        # Manual J.7.g: the application is denied "If the current balance is
        # zero". The annual electricity bill stands in for the balance owed.
        has_electric_bill = spm_unit("pre_subsidy_electricity_expense", period) > 0
        # Manual J.3.f.2: shelter residents and homeless households receive
        # only a security deposit.
        homeless = spm_unit.household("is_homeless", period)
        return (
            heating_type_reported
            & has_eligible_member
            & income_eligible
            & vulnerable
            & has_cooling_expense
            & has_electric_bill
            & ~homeless
        )

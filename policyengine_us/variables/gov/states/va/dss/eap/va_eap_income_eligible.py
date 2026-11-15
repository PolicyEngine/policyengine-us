from policyengine_us.model_api import *


def va_eap_income_test(spm_unit, period, limit):
    """Countable income at or below limit, or every member receives SSI."""
    income = spm_unit("va_eap_countable_income", period)
    # Manual B.6.a: "No eligible household shall exceed the income maximums
    # set by the VDSS, except households in which all members are SSI
    # recipients." 22VAC40-680-20(B)(1): income "must be at or below" the
    # limit.
    person = spm_unit.members
    receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
    all_ssi = spm_unit.all(receives_ssi)
    return (income <= limit) | all_ssi


class va_eap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Virginia EAP income eligible"
    documentation = "Countable income is at or below the income limit for the household size, or every household member receives SSI."
    reference = (
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/eap/Complete_Manual.pdf#page=28",
        "https://liheapch.acf.gov/docs/2026/state-plans/VA_Plan_2026.pdf#page=8",
        "https://law.lis.virginia.gov/admincode/title22/agency40/chapter680/section20/",
    )
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        limit = spm_unit("va_eap_income_limit", period)
        return va_eap_income_test(spm_unit, period, limit)

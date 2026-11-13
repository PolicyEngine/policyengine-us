from policyengine_us.model_api import *


class va_eap_cooling(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Virginia EAP cooling assistance electric bill payment"
    documentation = (
        "The electric bill up to the statewide maximum for the year. The annual "
        "electricity expense stands in for the balance owed on the electric "
        "account during the June to August application window. The first-come "
        "funding pool and the application window are not modeled."
    )
    reference = (
        # PDF pages 123, 127-129
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/eap/Complete_Manual.pdf#page=123",
        "https://liheapch.acf.gov/docs/2026/state-plans/VA_Plan_2026.pdf#page=12",
        "https://law.lis.virginia.gov/admincode/title22/agency40/chapter680/section63/",
    )
    defined_for = "va_eap_cooling_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.eap.cooling
        # Manual J.6: "The amount of assistance provided is the exact amount
        # of the bill not to exceed the appropriate maximum benefit." The
        # annual electricity bill stands in for the balance owed.
        bill = spm_unit("pre_subsidy_electricity_expense", period)
        return min_(bill, p.electric_bill_maximum)

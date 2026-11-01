from policyengine_us.model_api import *


class ne_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Nebraska LIHEAP eligible household size"
    defined_for = StateCode.NE
    reference = (
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/chapter-pdfs/476%20NAC%202%20(06-26-2022).pdf/1747#page=1",
        "https://dhhs.ne.gov/Documents/OBBB-SNAP-Changes-FAQ.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        # 476 NAC 2-002.02 incorporates SNAP citizenship/alien-status rules;
        # DHHS's OBBBA FAQ, Q12, expressly applies those changes to LIHEAP.
        # This is the immigration-status test, not SNAP work/student eligibility.
        # The shared variable applies the SNAP qualified-alien waiting period
        # and its exceptions; COFA status and case-specific recertification
        # timing remain gaps.
        # SPM units approximate energy-purchasing units (476 NAC 1-004.09).
        # LIHEAP-specific program violations and residency fraud are unmodeled.
        return add(
            spm_unit, period.first_month, ["is_snap_immigration_status_eligible"]
        )

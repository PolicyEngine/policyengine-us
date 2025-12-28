from policyengine_us.model_api import *


class oh_owf_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "Ohio OWF federal poverty guideline"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        "https://dam.assets.ohio.gov/image/upload/jfs.ohio.gov/OWF/tanf/2024%20TANF%20State%20Plan%20Combined.pdf#page=4",
        "https://codes.ohio.gov/ohio-revised-code/section-5107.10",  # (D)(2)
    )

    def formula(spm_unit, period, parameters):
        # Ohio uses FPL effective July 1 of each year per state law
        # "initial eligibility standards are annually indexed to fifty per cent
        # of the federal poverty level (FPL) effective July 1 of each year"
        n = spm_unit("spm_unit_size", period.this_year)
        state_group = spm_unit.household("state_group_str", period.this_year)
        year = period.start.year
        month = period.start.month
        # Use July 1 effective date (Ohio state fiscal year)
        if month >= 7:
            instant_str = f"{year}-07-01"
        else:
            instant_str = f"{year - 1}-07-01"
        p_fpg = parameters(instant_str).gov.hhs.fpg
        p1 = p_fpg.first_person[state_group] / MONTHS_IN_YEAR
        pn = p_fpg.additional_person[state_group] / MONTHS_IN_YEAR
        return p1 + pn * (n - 1)

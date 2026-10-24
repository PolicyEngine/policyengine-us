from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class vt_liheap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Vermont LIHEAP annual poverty guideline"
    documentation = (
        "Twelve times the whole-dollar monthly poverty guideline on which the "
        "P-2913 income maximums and the P-2914A percentage-of-poverty bands are "
        "built."
    )
    defined_for = StateCode.VT
    reference = (
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/ESD-Procedure-P2913.pdf",
        # PDF pages 1-3
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/ESD-Procedure-P2914A.pdf#page=1",
        "https://dcf.vermont.gov/esd/fuel/income-guidelines",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.vt.dcf.liheap
        size = spm_unit("vt_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        table_size = clip(size, 1, p.fpg_table_size)
        guideline = fpg(
            table_size, state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        additional_guideline = (
            fpg(
                table_size + 1,
                state_group,
                period,
                parameters,
                year_lag=p.fpg_year_lag,
            )
            - guideline
        )
        # Round the monthly guideline and the monthly additional-person amount
        # half up to the dollar separately.
        monthly_guideline = np.floor(guideline / MONTHS_IN_YEAR + 0.5)
        monthly_increment = np.floor(additional_guideline / MONTHS_IN_YEAR + 0.5)
        additional_people = max_(size - p.fpg_table_size, 0)
        monthly_amount = monthly_guideline + additional_people * monthly_increment
        return monthly_amount * MONTHS_IN_YEAR

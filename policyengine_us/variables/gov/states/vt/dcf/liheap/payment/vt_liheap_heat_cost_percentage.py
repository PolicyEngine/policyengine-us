from policyengine_us.model_api import *


class vt_liheap_heat_cost_percentage(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = "/1"
    label = "Vermont LIHEAP heat cost percentage"
    defined_for = StateCode.VT
    reference = (
        # PDF pages 39, 42
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2900-Seasonal-Fuel-Assistance.pdf#page=39",
        # PDF pages 1-3
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/ESD-Procedure-P2914A.pdf#page=1",
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/ESD-Procedure-P2915.pdf",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.vt.dcf.liheap.payment.heat_cost_percentage
        monthly_income = spm_unit("vt_liheap_income", period) / MONTHS_IN_YEAR
        monthly_guideline = spm_unit("vt_liheap_fpg", period) / MONTHS_IN_YEAR
        # Rule 2915(b) takes the percentage of poverty from the P-2914A table of
        # monthly dollar bands. Each threshold after the open first one tops the
        # band below it at that share of the monthly guideline, rounded up to the
        # dollar; income at or below a top stays in that band.
        # NOTE: Rounding to cents first keeps floating-point error from lifting
        # an exact dollar product to the next dollar.
        band = 0
        for rate in p.thresholds[1:]:
            top = np.ceil(np.round(rate * monthly_guideline, 2))
            band = band + (monthly_income > top)
        return np.array(p.amounts)[band]

from policyengine_us.model_api import *


class vt_reach_up_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont Reach Up payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/Benefits/VT-TANF-State-Plan-2024-2027.pdf",
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/ESD-Procedure-P2230A.pdf",
    )
    defined_for = StateCode.VT

    def formula(spm_unit, period, parameters):
        # Per Rule 2239 and Procedure P-2230A:
        # Payment standard =
        #   (basic needs + housing + special housing) × ratable reduction
        p = parameters(period).gov.states.vt.dcf.reach_up.allowance
        total_needs = add(
            spm_unit,
            period,
            [
                "vt_reach_up_basic_needs_allowance",
                "vt_reach_up_housing_allowance",
                "vt_reach_up_special_housing_allowance",
            ],
        )
        return total_needs * p.ratable_reduction

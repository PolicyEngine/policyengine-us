from policyengine_us.model_api import *


class vt_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont TANF payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/Benefits/VT-TANF-State-Plan-2024-2027.pdf",
    )
    defined_for = StateCode.VT

    def formula(spm_unit, period, parameters):
        # Per Rule 2239: Payment standard = (basic needs + housing) × ratable reduction
        p = parameters(period).gov.states.vt.dcf.tanf
        basic_needs = spm_unit("vt_tanf_basic_needs_allowance", period)
        housing = spm_unit("vt_tanf_housing_allowance", period)
        total_needs = basic_needs + housing
        return total_needs * p.benefit.ratable_reduction

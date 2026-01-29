from policyengine_us.model_api import *


class vt_reach_up_basic_needs_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont Reach Up basic needs allowance"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://law.justia.com/codes/vermont/title-33/chapter-11/section-1103/",
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
    )
    defined_for = StateCode.VT

    def formula(spm_unit, period, parameters):
        # Per Rule 2244.1: Basic needs by household size
        p = parameters(period).gov.states.vt.dcf.reach_up.allowance.basic_needs
        size = spm_unit("spm_unit_size", period.this_year)
        max_size = p.max_size
        # For sizes > max_size, add per-person amount for each additional person
        capped_size = min_(size, max_size)
        base_amount = p.amount[capped_size]
        additional_persons = max_(size - max_size, 0)
        return base_amount + additional_persons * p.additional_person

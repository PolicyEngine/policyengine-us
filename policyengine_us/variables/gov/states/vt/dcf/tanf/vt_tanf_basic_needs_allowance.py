from policyengine_us.model_api import *


class vt_tanf_basic_needs_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Vermont TANF basic needs allowance"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://law.justia.com/codes/vermont/title-33/chapter-11/section-1103/",
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
    )
    defined_for = StateCode.VT

    def formula(spm_unit, period, parameters):
        # Per Rule 2244.1: Basic needs by household size
        p = parameters(period).gov.states.vt.dcf.tanf.income
        size = spm_unit.nb_persons()
        # For sizes > 8, add per-person amount for each additional person
        capped_size = min_(size, 8)
        base_amount = p.basic_needs[capped_size]
        additional_persons = max_(size - 8, 0)
        return (
            base_amount + additional_persons * p.basic_needs_additional_person
        )

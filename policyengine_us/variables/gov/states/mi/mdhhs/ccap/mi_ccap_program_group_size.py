from policyengine_us.model_api import *


class mi_ccap_program_group_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Michigan CDC program group size"
    definition_period = MONTH
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/205.pdf#page=1"
    )

    def formula(spm_unit, period, parameters):
        # BEM 205: the CDC program group is the parent(s)/stepparent, the
        # children needing care, and their unmarried under-18 siblings —
        # roughly the SPM unit minus unrelated adults. We don't track each
        # adult's relationship to the child at the moment, so we use the full
        # SPM unit size. The RFT 270 income scale stops at family size 10, so
        # larger groups use the size-10 column.
        p = parameters(period).gov.states.mi.mdhhs.ccap.eligibility
        size = spm_unit("spm_unit_size", period.this_year)
        return min_(size, p.max_program_group_size)

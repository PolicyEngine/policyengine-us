from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class hi_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii LIHEAP annual income limit"
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.HI
    reference = (
        "https://www.hcapweb.org/wp-content/uploads/2026/04/H-HEAP-2026-Income-Eligibility.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("hi_liheap_household_size", period)
        group = spm_unit.household("state_group_str", period)
        p = parameters(period).gov.states.hi.dhs.liheap
        smi_limit = p.eligibility.smi_amount.calc(size)
        fpg_limit = p.eligibility.fpg_rate * fpg(
            max_(size, 1),
            group,
            period,
            parameters,
            year_lag=p.fpg_year_lag,
        )
        # The operational schedule's first ten amounts cannot all be reproduced
        # from SMI and a consistent rounding rule. Preserve the published dollars.
        # Its sizes 11-20 exactly match the lagged Hawaii FPG calculation;
        # continuing that percentage above size 20 is an unverified extension.
        limit = where(
            size <= p.eligibility.smi_max_household_size, smi_limit, fpg_limit
        )
        return where(size > 0, limit, 0)

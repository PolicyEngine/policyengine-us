from policyengine_us.model_api import *


class nd_ccap_child_support_deduction(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "North Dakota CCAP court-ordered support deduction"
    definition_period = MONTH
    defined_for = StateCode.ND
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(spm_unit, period, parameters):
        # The only deduction from countable income is court-ordered child or
        # spousal support paid by a counted unit member (400-28-65-30,
        # 400-28-70, NDAC 75-02-01.3-09). PolicyEngine tracks support paid as
        # annual person-level inputs, read here with the bare monthly period so
        # Core auto-divides them to a monthly amount. Private (non-court-
        # ordered) support and garnishment fees are not separately tracked.
        return add(spm_unit, period, ["child_support_expense", "alimony_expense"])

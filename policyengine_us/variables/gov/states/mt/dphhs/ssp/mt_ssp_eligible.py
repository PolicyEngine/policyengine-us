from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mt.dphhs.ssp.mt_ssp_payment_category import (
    MTSSPPaymentCategory,
)


class mt_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Montana SSP eligible"
    definition_period = MONTH
    defined_for = StateCode.MT
    reference = (
        "https://www.law.cornell.edu/regulations/montana/ARM-37-43-102",
        "https://www.law.cornell.edu/regulations/montana/ARM-37-43-103",
    )

    def formula(person, period, parameters):
        # ARM 37.43.102(2)(a) covers Group 2 (eligible-but-for-income),
        # so we gate on uncapped_ssi > 0 to admit recipients whose
        # countable income has zeroed the federal SSI payment.
        uncapped_ssi = person("uncapped_ssi", period)
        category = person("mt_ssp_payment_category", period)
        in_qualifying_arrangement = category != MTSSPPaymentCategory.NONE
        return (uncapped_ssi > 0) & in_qualifying_arrangement

from policyengine_us.model_api import *


class ca_oc_general_relief(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Orange County General Relief"
    definition_period = MONTH
    defined_for = "ca_oc_general_relief_eligible"
    reference = (
        "https://www.ssa.ocgov.com/sites/ssa/files/2025-03/Benefits_Services.pdf#page=1"
    )

    def formula(spm_unit, period, parameters):
        # The GR benefit is the maximum aid payment less all net countable
        # income (Sec 80.2.d, Sec 80.3.c-e). The grant cannot be negative.
        # We don't model the component-value deductions for in-kind aid met at
        # no cost (Sec 80.3.b) at the moment, because Orange County does not
        # publish the component-value dollar amounts.
        max_aid_payment = spm_unit("ca_oc_general_relief_max_aid_payment", period)
        countable_income = spm_unit("ca_oc_general_relief_countable_income", period)
        return max_(max_aid_payment - countable_income, 0)

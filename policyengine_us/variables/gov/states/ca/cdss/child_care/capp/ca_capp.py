from policyengine_us.model_api import *


class ca_capp(Variable):
    value_type = float
    entity = SPMUnit
    label = "California Alternative Payment Program subsidy"
    unit = USD
    definition_period = MONTH
    defined_for = "ca_capp_eligible"
    reference = "https://cdrv.org/cdr-programs-and-services/california-work-opportunity-and-responsibility-to-kids-calworks-alternative-payment-programs/"

    def formula(spm_unit, period, parameters):
        gross_payment = add(spm_unit, period, ["ca_capp_payment"])
        family_fee = spm_unit("ca_child_care_family_fee", period)
        return max_(gross_payment - family_fee, 0)

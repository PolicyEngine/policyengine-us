from policyengine_us.model_api import *


class ca_oc_general_relief_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Orange County General Relief countable income"
    unit = USD
    definition_period = MONTH
    defined_for = "in_oc"

    def formula(spm_unit, period, parameters):
        # Net earned and unearned income (Sec 70.2.o-p), plus liquid resources
        # over the $50 disregard, which Sec 70.2.g counts as income. Liquid
        # resources are a yearly stock, so read them for the full year rather
        # than letting period auto-divide them to a monthly amount.
        net_income = add(
            spm_unit, period, ["ca_oc_general_relief_countable_income_person"]
        )
        excess_liquid_resources = spm_unit(
            "ca_oc_general_relief_excess_liquid_resources", period.this_year
        )
        return net_income + excess_liquid_resources

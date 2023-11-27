from policyengine_us.model_api import *


class la_general_relief_base_amount(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Los Angeles County General Relief base amount"
    definition_period = MONTH
    defined_for = "la_general_relief_eligible"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"

    def formula(spm_unit, period, parameters):
        married = add(spm_unit, period, ["is_married"])
        p = parameters(period).gov.local.ca.la.general_relief
        base_amount = where(married, p.amount.married, p.amount.single)
        # The base amount phases out for recipients
        net_income = spm_unit("la_general_relief_net_income", period)
        excess_net_income = max_(net_income - p.phase_out.start, 0)
        divisor = p.phase_out.max - p.phase_out.start
        phase_out_rate = 1 - (min_(excess_net_income / divisor, 1))
        recipient = spm_unit("la_general_relief_recipient", period)
        phase_out_amount = where(recipient, base_amount * phase_out_rate, 0)
        print(excess_net_income / divisor)
        print(phase_out_rate)
        print(phase_out_amount)
        return max_(base_amount - phase_out_amount, 0)

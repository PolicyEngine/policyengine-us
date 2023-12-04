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
        phase_out_width = p.phase_out.max - p.phase_out.start
        reduction_percent = min_(excess_net_income / phase_out_width, 1)
        recipient = spm_unit("la_general_relief_recipient", period)
        # LA only reduces the amount for recipients, not new registrants.
        reduction = recipient * base_amount * reduction_percent
        return max_(base_amount - reduction, 0)

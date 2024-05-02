from policyengine_us.model_api import *


class az_hhs_tanf_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona Cash Assistance payment standard (A1 or A2)"
    definition_period = MONTH
    reference = "https://des.az.gov/services/child-and-family/cash-assistance/cash-assistance-ca-income-eligibility-guidelines"
    defined_for = StateCode.AZ


def formula(spm_unit, period, parameters):
    p = parameters(period).gov.states.az.hhs.tanf.eligibility.payment_standard
    # Whether the household has an obligation to pay allowable shelter costs
    shelter_cost = spm_unit("housing_cost", period)
    shelter_cost_standard = p.high
    no_shetler_cost_standard = p.low
    return (
        shelter_cost_standard if shelter_cost > 0 else no_shetler_cost_standard
    )

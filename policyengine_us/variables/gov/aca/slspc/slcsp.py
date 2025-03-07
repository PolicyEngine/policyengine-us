from policyengine_us.model_api import *


class slcsp(Variable):
    value_type = float
    entity = TaxUnit
    label = "Second-lowest ACA silver-plan cost"
    unit = USD
    definition_period = MONTH

    def formula(tax_unit, period, parameters):
        # Get the sum of individual age-rated premiums
        age_curve_amount = add(tax_unit, period, ["slcsp_person"])

        # Get the family tier amount from the variable we created
        family_tier_amount = tax_unit("slcsp_family_tier_amount", period)

        # Check if we're in a family tier state (NY or VT)
        state_code = tax_unit.household("state_code", period)
        family_tier_eligibility = parameters(
            period
        ).gov.aca.family_tier_states.states[state_code]

        # Use family tier calculation for NY and VT, otherwise use age curve
        return where(
            family_tier_eligibility, family_tier_amount, age_curve_amount
        )

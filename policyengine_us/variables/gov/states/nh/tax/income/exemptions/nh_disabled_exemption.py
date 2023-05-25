from policyengine_us.model_api import *


class nh_disabled_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire disabled exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Determine whether spouse is eligible.
        joint = filing_status == filing_status.possible_values.JOINT

        # Then get the NH disabled exemptions part of the parameter tree.
        p = parameters(
            period
        ).gov.states.nh.tax.income.exemptions

        # Get the individual disabled and age status.
        disabled_head = tax_unit("disabled_head", period)
        age_head = tax_unit("age_head", period) < p.disability_age_threshold
        head_eligible = disabled_head & age_head
        if joint: 
            # Get the individual's spouse disabled and age status.
            disabled_spouse = tax_unit("disabled_spouse", period) * joint
            age_spouse = (tax_unit("age_head", period) < p.disability_age_threshold) * joint 
            spouse_eligible = disabled_spouse & age_spouse

            # Check if eligible.
            eligible = (head_eligible | spouse_eligible).astype(int)

            # Calculate total blind exemption.
            return eligible * 2 * p.amount.disabled_addition
        
        else: 

            # Calculate total blind exemption.
            return head_eligible * p.amount.disabled_addition

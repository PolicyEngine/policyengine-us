from policyengine_us.model_api import *


class nh_old_age_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire old age exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Determine whether spouse is eligible.
        joint = filing_status == filing_status.possible_values.JOINT

        # Then get the NH old age exemptions part of the parameter tree.
        p = parameters(period).gov.states.nh.tax.income.exemptions

        # Get the individual age.
        age_head = tax_unit("age_head", period) 

        # Check if the individual's eligiblity.
        head_eligible = (age_head >= p.old_age_eligibility).astype(int)

        # Get the individual's spouse age.
        age_spouse = tax_unit("age_spouse", period) * joint

        # Check if the individual spouse's eligiblity.
        spouse_eligible = (age_spouse >= p.old_age_eligibility).astype(int)

        # Calculate total blind exemption.
        return (head_eligible + spouse_eligible) * p.amount.old_age_addition
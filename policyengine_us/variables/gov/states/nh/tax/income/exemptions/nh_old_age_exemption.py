from policyengine_us.model_api import *


class nh_old_age_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire old age exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        # Then get the NH old age exemptions part of the parameter tree.
        p = parameters(period).gov.states.nh.tax.income.exemptions

        # Check if the individual's eligiblity.
        head_eligible = (
            tax_unit("age_head", period) >= p.old_age_eligibility
        ).astype(int)

        # Check if the individual spouse's eligiblity.
        spouse_eligible = (
            tax_unit("age_spouse", period) >= p.old_age_eligibility
        ).astype(int)

        # Calculate total blind exemption.
        return (head_eligible + spouse_eligible) * p.amount.old_age_addition

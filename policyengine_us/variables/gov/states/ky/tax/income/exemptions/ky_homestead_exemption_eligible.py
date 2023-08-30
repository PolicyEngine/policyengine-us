from policyengine_us.model_api import *


class ky_homestead_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Kentucky homestead exemptions"
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ky.tax.income.exemptions.homestead

        # Get the individual disabled and age status.
        disabled_head = tax_unit("disabled_head", period)
        age_head = tax_unit("age_head", period) < p.disability_age_threshold
        head_eligible = (disabled_head & age_head).astype(int)

        # Calculate total exemption.
        return head_eligible * p.amount.disabled_addition

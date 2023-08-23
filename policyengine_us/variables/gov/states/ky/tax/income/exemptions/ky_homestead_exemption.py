from policyengine_us.model_api import *


class ky_homestead_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky homestead exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ky.tax.income.exemptions.homestead

        # Get the individual filer's age.
        age_head = tax_unit("age_head", period)
        
        # Get the disability status of the head of the household.
        is_disabled = tax_unit("is_disabled", period)

        # Determine if head of (filer) is eligible considering age and disability.
        head_eligible = (age_head >= p.age_threshold) & is_disabled
        eligible_count = head_eligible.astype(int)
        
        return eligible_count * p.amount
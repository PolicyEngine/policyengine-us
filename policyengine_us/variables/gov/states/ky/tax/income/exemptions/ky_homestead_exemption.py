from policyengine_us.model_api import *


class ky_homestead_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky homestead exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.KY.tax.income.exemptions.homestead
        # Get the individual filer's age.
        age_head = tax_unit("age_head", period)
        # Determine if head of (filer) is eligible.
        head_eligible = (age_head >= p.age_threshold).astype(int)
        eligible_count = head_eligible.astype(int)
        return eligible_count * p.amount
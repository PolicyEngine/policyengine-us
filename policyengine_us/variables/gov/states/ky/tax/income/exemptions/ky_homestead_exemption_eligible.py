from policyengine_us.model_api import *


class ky_homestead_exemption_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Kentucky homestead exemption"
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ky.tax.income.exemptions.homestead

        # Get the individual disabled and age status.
        disabled_head = tax_unit("disabled_head", period)
        age_head = tax_unit("age_head", period) >= p.age_threshold

        return disabled_head | age_head

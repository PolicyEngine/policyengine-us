from policyengine_us.model_api import *


class basic_health_program_adjusted_reference_premium(Variable):
    value_type = float
    entity = TaxUnit
    label = "Basic Health Program adjusted reference premium"
    unit = USD
    definition_period = MONTH
    reference = "https://www.medicaid.gov/basic-health-program"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.hhs.basic_health_program.payment
        return (
            tax_unit("basic_health_program_reference_premium", period)
            * p.premium_adjustment_factor
            * p.population_health_factor
            * p.waiver_factor
        )

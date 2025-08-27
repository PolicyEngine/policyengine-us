from policyengine_us.model_api import *


class id_liheap_seasonal_heating_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP seasonal heating assistance amount"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.ID
    documentation = "Monthly seasonal heating assistance payment amount"
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
    ]

    def formula(spm_unit, period, parameters):
        # Seasonal heating payment for eligible households
        eligible = spm_unit("id_liheap_seasonal_heating_eligible", period)

        # Get benefit parameters
        p = parameters(period).gov.states.id.idhw.liheap.seasonal_benefit

        # For simulation, provide minimum benefit to all eligible households
        # In reality, benefit amount depends on income, household size, energy burden
        return where(eligible, p.minimum, 0)

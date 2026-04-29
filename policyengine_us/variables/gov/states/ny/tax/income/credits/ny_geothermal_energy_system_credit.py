from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ny_geothermal_energy_system_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York geothermal energy system equipment credit"
    documentation = "The tax credit for a qualified purchase or lease of geothermal energy system equipment, with a 5-year carryover."
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (g)(2)(C)(9)(g-4)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ny.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ny_income_tax_before_credits",
            "ny_geothermal_energy_system_credit",
            "ny_geothermal_energy_system_credit_potential",
        )

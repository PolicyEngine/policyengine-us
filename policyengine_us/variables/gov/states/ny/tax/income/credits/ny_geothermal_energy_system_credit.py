from policyengine_us.model_api import *


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
        qualified_expenditures = tax_unit(
            "ny_qualified_geothermal_energy_system_expenditures", period
        )
        p = parameters(
            period
        ).gov.states.ny.tax.income.credits.geothermal_energy_system
        uncapped_credit = qualified_expenditures * p.rate
        return min_(uncapped_credit, p.cap)

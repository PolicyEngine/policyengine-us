from policyengine_us.model_api import *


class ny_solar_energy_systems_equipment_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York solar energy systems equipment credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (g)(2)(C)(9)(g-1)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        qualified_expenditures = tax_unit(
            "ny_qualified_solar_energy_systems_equipment_expenditures", period
        )
        p = parameters(
            period
        ).gov.states.ny.tax.income.credits.solar_energy_systems_equipment
        uncapped_credit = qualified_expenditures * p.rate
        return min_(uncapped_credit, p.cap)

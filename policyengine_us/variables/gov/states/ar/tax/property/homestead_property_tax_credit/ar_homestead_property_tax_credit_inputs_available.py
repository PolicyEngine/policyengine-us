from policyengine_us.model_api import *


class ar_homestead_property_tax_credit_inputs_available(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    default_value = False
    label = "Inputs for the Arkansas homestead property tax credit are available"
    reference = "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F2023R%2FPublic%2FACT541.pdf#page=1"

    # Pre-2025 assessment years are unsupported and retain the false default;
    # this implementation date is not the statutory program's starting date.
    def formula_2025_01_01(tax_unit, period, parameters):
        facts_available = tax_unit(
            "ar_homestead_property_tax_credit_facts_available", period
        )
        qualified_property_taxes = tax_unit(
            "ar_homestead_property_tax_credit_qualified_property_taxes", period
        )
        return facts_available & (qualified_property_taxes >= 0)

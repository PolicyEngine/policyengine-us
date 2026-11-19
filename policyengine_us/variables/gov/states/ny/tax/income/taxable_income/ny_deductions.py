from policyengine_us.model_api import *
from policyengine_us.tools.period_branch import has_input
from policyengine_us.tools.state_itemization import state_itemization_uses_itemized


class ny_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY income deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/613"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        return max_(
            tax_unit("ny_itemized_deductions", period),
            tax_unit("ny_standard_deduction", period),
        )

    def formula_2018(tax_unit, period, parameters):
        itemized = tax_unit("ny_itemized_deductions", period)
        standard = tax_unit("ny_standard_deduction", period)
        # Retain the historic automatic larger-amount calculation unless a
        # state election was filed. Section 613 recomputes smaller items.
        automatic = (
            tax_unit("ny_itemizes", period)
            if has_input(tax_unit.simulation, "ny_itemizes", period)
            else itemized >= standard
        )
        method = tax_unit("state_deduction_method", period)
        use_items = state_itemization_uses_itemized(method, automatic)
        return where(use_items, max_(itemized, standard), standard)

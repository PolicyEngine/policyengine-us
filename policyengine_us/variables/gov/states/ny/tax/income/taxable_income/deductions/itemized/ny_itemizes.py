from policyengine_us.model_api import *
from policyengine_us.tools.state_itemization import (
    joint_itemization_is_enabled,
    state_itemization_uses_itemized,
)


class ny_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Itemizes New York deductions"
    documentation = (
        "New York allows an independent state election from 2018. Under Tax "
        "Law section 613 the department recomputes a smaller itemized "
        "deduction using the standard deduction."
    )
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = "https://www.nysenate.gov/legislation/laws/TAX/613"

    def formula(tax_unit, period, parameters):
        federal_itemizes = tax_unit("tax_unit_itemizes", period)
        standard_deduction = tax_unit("ny_standard_deduction", period)
        itemized_deductions = tax_unit("ny_itemized_deductions", period)
        return federal_itemizes & (itemized_deductions >= standard_deduction)

    def formula_2018(tax_unit, period, parameters):
        automatic = (
            True
            if joint_itemization_is_enabled(period, parameters)
            else tax_unit("tax_unit_itemizes", period)
        )
        standard = tax_unit("ny_standard_deduction", period)
        itemized = tax_unit("ny_itemized_deductions", period)
        method = tax_unit("state_deduction_method", period)
        elects_itemized = state_itemization_uses_itemized(method, automatic)
        return elects_itemized & (itemized >= standard)

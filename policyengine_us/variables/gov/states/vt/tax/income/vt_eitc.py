from policyengine_us.model_api import *


class vt_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont earned income tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf#page=1"
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.vt.tax.income.credits.eitc

        # S.51 (2025): Enhanced EITC for workers without children
        enhanced_structure_applies = p.enhanced_structure.in_effect

        # Check if tax unit has qualifying children for EITC
        person = tax_unit.members
        is_child_dependent = person("is_child_dependent", period)
        has_qualifying_children = tax_unit.any(is_child_dependent)

        # Different match rates for workers with and without children (2025+)
        match_rate = where(
            p.match_without_children, 1.0, 0.0
        )
        enhanced_rate = where(
            has_qualifying_children,
            p.match,  # 38% for workers with children
            match_rate  # 100% for workers without children if enabled
        )

        # Pre-2025: Use standard match rate for all workers
        standard_rate = p.match

        rate = where(
            enhanced_structure_applies,
            enhanced_rate,
            standard_rate,
        )

        return federal_eitc * rate

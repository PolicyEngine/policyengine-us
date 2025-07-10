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
        if period.start.year >= 2025:
            # Check if tax unit has qualifying children for EITC
            person = tax_unit.members
            age = person("age", period)
            is_child = age < 19  # Simplified check for qualifying children
            has_qualifying_children = tax_unit.any(is_child)

            # Different match rates for workers with and without children
            rate = where(
                has_qualifying_children,
                p.match,  # 38% for workers with children
                p.match_without_children,  # 100% for workers without children
            )
        else:
            rate = p.match

        return federal_eitc * rate

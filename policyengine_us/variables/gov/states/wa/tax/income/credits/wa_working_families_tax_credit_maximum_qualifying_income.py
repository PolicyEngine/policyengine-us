from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    calculate_eitc_max_agi_limit,
)


class wa_working_families_tax_credit_maximum_qualifying_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Washington Working Families Tax Credit maximum qualifying income"
    unit = USD
    definition_period = YEAR
    reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=59"
    defined_for = StateCode.WA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.wa.tax.income.credits.working_families_tax_credit.maximum_qualifying_income
        frozen_eitc = parameters.gov.irs.credits.eitc("2022-06-09")
        person = tax_unit.members
        federal_child_count = tax_unit("eitc_child_count", period)
        washington_child_count = tax_unit.sum(
            person("is_qualifying_child_dependent", period) & person("has_tin", period)
        )
        child_count = max_(federal_child_count, washington_child_count)
        federal_max_agi = calculate_eitc_max_agi_limit(
            tax_unit, period, frozen_eitc, child_count
        )
        if not p.in_effect:
            return federal_max_agi
        size = tax_unit("tax_unit_size", period)
        capped_size = min_(size, p.max_assistance_unit_size)
        cash_assistance_limit = (
            p.cash_assistance_need_standard[capped_size] * MONTHS_IN_YEAR
        )
        return max_(federal_max_agi, cash_assistance_limit)

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
    reference = (
        "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=60",
        # RCW 82.08.0206(2)(e)-(f): income limit and qualifying children,
        # including children with ITINs.
        "https://app.leg.wa.gov/RCW/default.aspx?cite=82.08.0206",
        "https://www.law.cornell.edu/uscode/text/26/152#c_3_B",
        # DOR's age waiver and the application's disability/SSN-or-ITIN fields.
        "https://workingfamiliescredit.wa.gov/sites/default/files/2024-01/WFTC_AppInstr_English_2023.pdf#page=5",
        "https://workingfamiliescredit.wa.gov/sites/default/files/2024-01/WFTC_app_2023_English.pdf#page=3",
    )
    defined_for = StateCode.WA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.wa.tax.income.credits.working_families_tax_credit.maximum_qualifying_income
        # RCW 82.08.0206(2)(d) pins Washington's WFTC to the federal EITC rules
        # as in effect on June 9, 2022, but that Internal Revenue Code still
        # contains the EITC inflation-adjustment provisions (IRC 26 U.S.C.
        # 32(j)), so the maximum-qualifying-income ceiling indexes to the
        # current tax year. Washington DOR publishes the current-year federal
        # EITC income limits (e.g. $53,120 for married-filing-jointly with one
        # qualifying child in 2023). The federal EITC structure is unchanged
        # from 2022 through 2024, so the current-period parameters carry only
        # the annual indexing, not a post-2022 rule change.
        eitc = parameters(period).gov.irs.credits.eitc
        person = tax_unit.members
        federal_child_count = tax_unit("eitc_child_count", period)
        # Apply the IRC 152(c)(3)(B) age waiver to ITIN children too, using
        # the same qualifying-child count as the WFTC amount formula.
        is_disabled_dependent = person("is_tax_unit_dependent", period) & person(
            "is_permanently_and_totally_disabled", period
        )
        washington_child_count = tax_unit.sum(
            (person("is_qualifying_child_dependent", period) | is_disabled_dependent)
            & person("has_tin", period)
        )
        child_count = max_(federal_child_count, washington_child_count)
        federal_max_agi = calculate_eitc_max_agi_limit(
            tax_unit, period, eitc, child_count
        )
        if not p.in_effect:
            return federal_max_agi
        size = tax_unit("tax_unit_size", period)
        capped_size = min_(size, p.max_assistance_unit_size)
        cash_assistance_limit = (
            p.cash_assistance_need_standard[capped_size] * MONTHS_IN_YEAR
        )
        return max_(federal_max_agi, cash_assistance_limit)

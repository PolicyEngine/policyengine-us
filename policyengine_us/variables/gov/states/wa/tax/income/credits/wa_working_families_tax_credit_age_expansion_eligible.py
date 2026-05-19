from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    calculate_eitc_amount_from_parameters,
)


class wa_working_families_tax_credit_age_expansion_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Washington Working Families Tax Credit via age expansion"
    definition_period = YEAR
    reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=60"
    defined_for = StateCode.WA

    def formula(tax_unit, period, parameters):
        # ESSB 6346 Sec. 901(2)(a)(ii)(D): individuals who would otherwise
        # qualify for EITC except for age can qualify if at least age 18.
        wftc = parameters(
            period
        ).gov.states.wa.tax.income.credits.working_families_tax_credit
        p = wftc.age_expansion

        expansion_in_effect = p.in_effect
        person = tax_unit.members
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        filer_meets_min_age = (age_head >= p.min_age) | (age_spouse >= p.min_age)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        has_tin = person("has_tin", period)
        filers_have_tin = tax_unit.sum(is_head_or_spouse & ~has_tin) == 0
        child_count = tax_unit.sum(
            person("is_qualifying_child_dependent", period) & has_tin
        )
        # RCW 82.08.0206(2)(d) freezes WFTC to the federal EITC rules as of
        # wftc.federal_eitc_snapshot_date (currently 2022-06-09).
        frozen_eitc = parameters.gov.irs.credits.eitc(wftc.federal_eitc_snapshot_date)
        frozen_investment_income_eligible = (
            tax_unit("eitc_relevant_investment_income", period)
            <= frozen_eitc.phase_out.max_investment_income
        )
        eitc_amount_before_take_up = calculate_eitc_amount_from_parameters(
            tax_unit, period, frozen_eitc, child_count
        )

        return (
            expansion_in_effect
            & filer_meets_min_age
            & frozen_investment_income_eligible
            & filers_have_tin
            & (eitc_amount_before_take_up > 0)
        )

from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    eitc_filing_requirement_met,
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
        #
        # Methodology note (age): Sec. 901(2)(a)(ii)(D) refers to age as of the
        # prior tax year. PolicyEngine evaluates a single period, so this
        # formula uses current-period age_head / age_spouse as an approximation.
        # The off-by-one-year edge case (filer turning min_age during the tax
        # year) is not modeled.
        #
        # No separate-filer (MFS) guard is applied here because the WFTC is a
        # state-only credit that, by design, does not honor the federal MFS
        # bar; the main wa_working_families_tax_credit variable's state-only
        # path treats `separate` filers as eligible.
        p = parameters(
            period
        ).gov.states.wa.tax.income.credits.working_families_tax_credit.age_expansion

        expansion_in_effect = p.in_effect
        person = tax_unit.members
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        filer_meets_min_age = (age_head >= p.min_age) | (age_spouse >= p.min_age)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        has_tin = person("has_tin", period)
        filers_have_tin = tax_unit.sum(is_head_or_spouse & ~has_tin) == 0
        # ESSB 6346 Sec. 901(2)(a)(ii)(D) is the childless-by-age expansion
        # path: it covers filers who would qualify for the EITC except for
        # age. Because it does not depend on qualifying children, no child
        # count (and therefore no IRC 152(c)(3)(B) disabled-dependent test) is
        # needed here; the disabled-dependent handling lives in the main
        # wa_working_families_tax_credit child_count.
        # RCW 82.08.0206(2)(d) pins WFTC to the federal EITC rules as in
        # effect on June 9, 2022; this snapshot date is a statutory literal.
        frozen_eitc = parameters.gov.irs.credits.eitc("2022-06-09")
        frozen_investment_income_eligible = (
            tax_unit("eitc_relevant_investment_income", period)
            <= frozen_eitc.phase_out.max_investment_income
        )
        earnings = tax_unit("filer_adjusted_earnings", period)
        agi = tax_unit("adjusted_gross_income", period)
        income_eligible = (earnings > 0) & (
            max_(earnings, agi)
            <= tax_unit(
                "wa_working_families_tax_credit_maximum_qualifying_income", period
            )
        )
        is_filer = eitc_filing_requirement_met(tax_unit, period)
        takes_up_eitc = tax_unit("takes_up_eitc", period)

        return (
            expansion_in_effect
            & filer_meets_min_age
            & income_eligible
            & frozen_investment_income_eligible
            & filers_have_tin
            & is_filer
            & takes_up_eitc
        )

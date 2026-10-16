from policyengine_us.model_api import *


class in_eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Indiana earned income tax credit eligibility status"
    unit = USD
    definition_period = YEAR
    reference = "https://iga.in.gov/laws/2021/ic/titles/6#6-3.1-21"
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income
        # check federal eitc receipt
        gets_federal_eitc = tax_unit("eitc", period) > 0
        if not p.credits.earned_income.decoupled:
            return gets_federal_eitc
        if p.credits.earned_income.static_conformity_in_effect:
            # IC 6-3.1-21-6(a) allows the credit to an individual "eligible
            # for an earned income tax credit under Section 32 of the
            # Internal Revenue Code as in effect on January 1, 2023" (IC
            # 6-3-1-11; January 1, 2026 from TY2026 per SEA 243 (2025)).
            # Section 32 as in effect on that date indexes its earned income,
            # phaseout and investment income amounts to the calendar year in
            # which the taxable year begins (26 U.S.C. 32(j)(1)), and
            # IC 6-3.1-21-6(e) applies the same cost of living adjustments.
            # Section 32 has not been amended since, so eligibility under
            # the conformity-date text is eligibility for the current-year
            # federal credit, not for the credit with the snapshot date's
            # dollar amounts. The IT-40 booklet (Schedule 5, line 6) also
            # requires that the filer "be eligible for and have claimed an
            # EIC on your federal tax return".
            return gets_federal_eitc
        # if Indiana EITC is decoupled from federal EITC
        # ... check separate filing status
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        # ... check age eligibility for childless taxpayers
        is_childless = tax_unit("eitc_child_count", period) == 0
        min_age = p.credits.earned_income.childless.min_age
        max_age = p.credits.earned_income.childless.max_age
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        head_age_eligible = (age_head >= min_age) & (age_head <= max_age)
        spouse_age_eligible = (age_spouse >= min_age) & (age_spouse <= max_age)
        married = filing_status == filing_status.possible_values.JOINT
        age_eligible = where(
            married, head_age_eligible | spouse_age_eligible, head_age_eligible
        )
        childless_age_eligible = where(is_childless, age_eligible, True)
        # ... check investment income eligibility
        invinc = tax_unit("eitc_relevant_investment_income", period)
        invinc_limit = p.credits.earned_income.investment_income_limit
        invinc_eligible = invinc <= invinc_limit
        # ... determine Indiana EITC eligibility status
        in_eligible = ~separate & childless_age_eligible & invinc_eligible
        return gets_federal_eitc & in_eligible

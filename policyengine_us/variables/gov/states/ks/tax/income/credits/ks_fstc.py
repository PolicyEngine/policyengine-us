from policyengine_us.model_api import *


class ks_fstc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas food sales tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        # K.S.A. 79-32,271(d): $125 "for every exemption claimed on the
        # taxpayer's federal income tax return".
        "https://kslegislature.gov/b2025_26/laws/079_000_0000_chapter/079_032_0000_article/079_032_0271_section/079_032_0271_k/",
        "https://kslegislature.gov/li_2022/b2021_22/measures/documents/hb2106_enrolled.pdf#page=2",
        "https://www.ksrevenue.gov/pdf/ip21.pdf#page=6",
        "https://www.ksrevenue.gov/pdf/ip22.pdf#page=6",
        "https://www.ksrevenue.gov/pdf/ip23.pdf#page=6",
        "https://www.ksrevenue.gov/pdf/ip24.pdf#page=6",
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.credits
        # K.S.A. 79-32,271(d) counts "every exemption claimed on the
        # taxpayer's federal income tax return": each filer whom no other
        # taxpayer may claim (IRC 151(d)(2)), plus dependent children under
        # 18, since dependents 18 or older do not count. The K-40 instructions
        # instead carry the Kansas exemption count (Line E), with its
        # filing-status allowances from 2024; the statute governs.
        filers = tax_unit("head_spouse_count_not_dependent_elsewhere", period)
        # A return on which the filer (or, if joint, either spouse) can be
        # claimed has no dependents (IRC 152(b)(1)), unless the would-be
        # claimant meets the filing exception (Publication 501, Dependent
        # Taxpayer Test). This limits only the children, not an unclaimable
        # spouse's own exemption.
        filer_is_dependent = tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        person = tax_unit.members
        is_child = person("age", period) < p.food_sales_tax.child_age
        is_child_dependent = person("is_tax_unit_dependent", period) & is_child
        child_dependents = where(
            filer_is_dependent, 0, tax_unit.sum(is_child_dependent)
        )
        # Eligibility: a dependent child, an elderly filer, or a blind or
        # disabled filer.
        min_adult_age = p.food_sales_tax.min_adult_age
        elderly_head = tax_unit("age_head", period) >= min_adult_age
        elderly_spouse = tax_unit("age_spouse", period) >= min_adult_age
        eligible_age = elderly_head | elderly_spouse
        eligible_blind_disabled = (
            tax_unit("blind_head", period)
            | tax_unit("blind_spouse", period)
            | tax_unit("head_is_disabled", period)
            | tax_unit("spouse_is_disabled", period)
        )
        eligible_unit = (child_dependents > 0) | eligible_age | eligible_blind_disabled
        fagi = tax_unit("adjusted_gross_income", period)
        eligible_income = fagi <= p.food_sales_tax.agi_limit
        eligible = eligible_unit & eligible_income
        exemptions = filers + child_dependents
        return eligible * exemptions * p.food_sales_tax.amount

from policyengine_us.model_api import *


class dependent_care_assistance_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Dependent care assistance excluded from gross income"
    documentation = (
        "Amount of employer-provided dependent care benefits excludable from "
        "gross income under IRC section 129. This is the amount that reduces "
        "the section 21(c) CDCC dollar limit (Form 2441 Part III)."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # Exclusion and its two limits.
        "https://www.law.cornell.edu/uscode/text/26/129#a_2",  # Dollar cap.
        "https://www.law.cornell.edu/uscode/text/26/129#a_2_C",  # Marital status.
        "https://www.law.cornell.edu/uscode/text/26/129#b",  # Earned income limit.
        # Form 2441 line 19 (spouse's earned income).
        "https://www.irs.gov/pub/irs-prior/i2441--2025.pdf#page=5",
        # ARPA section 9632 temporarily increased the cap for 2021.
        "https://www.govinfo.gov/content/pkg/PLAW-117publ2/pdf/PLAW-117publ2.pdf#page=158",
        # Form 2441 Part III lines 12-26 compute the excluded benefit.
        "https://www.irs.gov/pub/irs-prior/f2441--2021.pdf#page=2",
        "https://www.irs.gov/instructions/i2441",
    )

    def formula(tax_unit, period, parameters):
        # Total employer-provided dependent care benefits (Form 2441 line 12,
        # W-2 box 10).
        benefits = add(tax_unit, period, ["dependent_care_employer_benefits"])
        p = parameters(period).gov.irs.gross_income.dependent_care_assistance_programs
        # Section 129(a)(2)(A) dollar cap by filing status (Form 2441 line 21;
        # $5,000, $2,500 MFS; $10,500 / $5,250 for 2021 under section
        # 129(a)(2)(D); raised to $7,500 / $3,750 after 2025 by OBBBA).
        # Section 129(a)(2)(C) determines marital status under section
        # 21(e)(3) and (4), so a separate filer treated as unmarried under
        # 21(e)(4) takes the unmarried cap, not the MFS half.
        filing_status = tax_unit("filing_status", period)
        treated_as_unmarried = tax_unit("cdcc_treated_as_unmarried", period)
        dollar_cap = where(
            treated_as_unmarried,
            p.reduction_amount["SINGLE"],
            p.reduction_amount[filing_status],
        )
        # Section 129(b) earned-income limitation: the exclusion cannot exceed
        # the taxpayer's earned income, or, for a taxpayer married at the end
        # of the year, the lesser of the taxpayer's and the spouse's earned
        # income (Form 2441 lines 18-19). min_head_spouse_earned returns the
        # taxpayer's earnings when unmarried and the lesser of the two when
        # married filing jointly.
        earned_income_limit = tax_unit("min_head_spouse_earned", period)
        # A married taxpayer who does not file jointly (a separate filer, or a
        # separated filer filing as head of household) is still married for
        # section 129(b)(1)(B). Section 129(a)(2)(C) imports the section
        # 21(e)(4) rule for living apart "for purposes of this paragraph",
        # the dollar cap, and section 129(b) does not import it. The Form 2441
        # line 19 instructions let a filer treated as unmarried under that
        # rule enter their own earned income; the model follows the statute
        # and uses the spouse's earned income, absent_spouse_earned_income.
        separate = filing_status == filing_status.possible_values.SEPARATE
        joint = filing_status == filing_status.possible_values.JOINT
        person = tax_unit.members
        separated = tax_unit.any(
            person("is_tax_unit_head_or_spouse", period)
            & person("is_separated", period)
        )
        married_not_joint = separate | (separated & ~joint)
        earned_income_limit = where(
            married_not_joint,
            min_(earned_income_limit, tax_unit("absent_spouse_earned_income", period)),
            earned_income_limit,
        )
        return min_(benefits, min_(dollar_cap, earned_income_limit))

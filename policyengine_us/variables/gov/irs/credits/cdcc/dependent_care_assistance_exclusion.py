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
        "https://www.law.cornell.edu/uscode/text/26/129#b",  # Earned income limit.
        # Form 2441 Part III lines 12-26 compute the excluded benefit.
        "https://www.irs.gov/instructions/i2441",
    )

    def formula(tax_unit, period, parameters):
        # Total employer-provided dependent care benefits (Form 2441 line 12,
        # W-2 box 10).
        benefits = add(tax_unit, period, ["dependent_care_employer_benefits"])
        p = parameters(period).gov.irs.gross_income.dependent_care_assistance_programs
        # Section 129(a)(2)(A) dollar cap by filing status (Form 2441 line 21;
        # $5,000, $2,500 MFS, raised to $7,500 / $3,750 after 2025 by OBBBA).
        filing_status = tax_unit("filing_status", period)
        dollar_cap = p.reduction_amount[filing_status]
        # Section 129(b) earned-income limitation: the exclusion cannot exceed
        # the taxpayer's earned income, or, for a married taxpayer, the lesser
        # of the taxpayer's and spouse's earned income (Form 2441 lines 18-19).
        # min_head_spouse_earned returns the taxpayer's earnings when unmarried
        # and the lesser of the two when married filing jointly.
        earned_income_limit = tax_unit("min_head_spouse_earned", period)
        return min_(benefits, min_(dollar_cap, earned_income_limit))

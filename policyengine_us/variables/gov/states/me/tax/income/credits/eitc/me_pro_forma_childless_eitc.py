from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    eitc_section_911_eligible,
    federal_eitc_tax_unit,
    pro_forma_federal_eitc,
)


class me_pro_forma_childless_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine pro forma federal EITC for the childless age expansion"
    unit = USD
    documentation = (
        "Federal earned income credit computed for the 18-24 childless "
        "cohort Maine restores under 36 M.R.S. § 5219-S(5)-(6), ignoring the "
        "federal minimum-age floor. The other federal § 32 requirements "
        "(earnings, phase-out, investment income, taxpayer identification, "
        "the bar on section 911 claimants) still apply, as does any reform of "
        "the federal credit. From 2021 an ITIN or any Social Security number "
        "meets the identification requirement (§ 5219-S(7)). Like the federal "
        "credit, it is computed on the AGI of the return as filed; unlike it, "
        "it applies no take-up, filing condition or separate-filer rule."
    )
    definition_period = YEAR
    reference = (
        "https://legislature.maine.gov/statutes/36/title36sec5219-S.html",
        "https://www.law.cornell.edu/uscode/text/26/32#c_1_C",
        # Maine Revenue Services, Worksheet for Earned Income Tax Credit (2024,
        # revised December 2024): complete Steps 1 through 6 of the federal
        # Form 1040 line 27 instructions, changing only the TIN and age answers.
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/24_earned_income_cred_ff_0.pdf",
        # 2024 Form 1040 instructions, EIC Step 1, question 3: "Are you filing
        # Form 2555 ...? Yes. STOP You can't take the credit."
        "https://www.irs.gov/pub/irs-prior/i1040gi--2024.pdf#page=38",
    )
    defined_for = "me_childless_eitc_age_eligible"

    def formula(tax_unit, period, parameters):
        # § 5219-S(5): the credit "must be calculated in the same manner as it
        # would be calculated if that individual were eligible for a federal
        # earned income credit." Evaluate the federal EITC with its
        # eligibility replaced by the conditions below: the demographic (age)
        # gate dropped, the investment-income and identification
        # requirements of § 32 kept. From 2021, § 5219-S(7) lets an ITIN or
        # any Social Security number meet the identification requirement of
        # § 32(c)(1)(E).
        p = parameters(period).gov.states.me.tax.income.credits.eitc
        federal = federal_eitc_tax_unit(tax_unit, period, p.itin_eligible)
        # § 5219-S(6) also requires the qualifications of IRC
        # 32(c)(1)(A)(ii)(III): the filer may not be a dependent of another
        # taxpayer, and on a joint return neither spouse may be (Publication
        # 596, Rule 12).
        dependent_filer = federal(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        # § 5219-S(6) gives "eligible individual" "the same meaning as under
        # Section 32(c)(1) of the Code", and § 32(c)(1)(C) excludes an
        # individual who claims the benefits of section 911. The Maine
        # worksheet keeps the federal Form 2555 stop.
        eligible = (
            federal("eitc_investment_income_eligible", period)
            & federal("filer_meets_eitc_identification_requirements", period)
            & ~dependent_filer
            & eitc_section_911_eligible(federal, period)
        )
        return pro_forma_federal_eitc(federal, period, "me_pro_forma_eitc", eligible)

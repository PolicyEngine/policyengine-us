from policyengine_us.model_api import *


class co_social_security_subtraction_indv(Variable):
    value_type = float
    entity = Person
    label = "Colorado social security subtraction for eligible individuals"
    defined_for = "co_social_security_subtraction_indv_eligible"
    unit = USD
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12",
        "https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-104/",
        # C.R.S. 39-22-104(4)(f)(III)(A)
        "https://leg.colorado.gov/sites/default/files/2024a_1142_signed.pdf#page=2",
        "https://tax.colorado.gov/sites/tax/files/documents/Book104_2025.pdf#page=18",
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.tax.income.subtractions.pension
        if not p.social_security_subtraction_available:
            return 0
        taxable_social_security = person("taxable_social_security", period)
        social_security_survivors = person("social_security_survivors", period)
        age = person("age", period)
        # Only head and spouse can claim this subtraction
        eligible_social_security_survivors = social_security_survivors
        eligible_taxable_social_security = taxable_social_security
        # If the filer is 65 or older, they can claim full subtarction
        # If the filer is between 65 and 55, they can claim a capped amount
        cap = p.cap.younger
        # HB24-1142 (C.R.S. 39-22-104(4)(f)(III)(A)): for tax years beginning on
        # or after 2025-01-01, a filer aged 55-64 whose taxable Social Security
        # benefits exceed the $20,000 cap and whose federal AGI is at or below
        # $75,000 (filing individually) or $95,000 (filing jointly) has the cap
        # "increased to an amount equal to the total amount of such social
        # security benefits." The effective cap for the middle bracket then
        # equals the taxable Social Security amount, so the full amount is
        # subtracted. Before 2025 the AGI limit parameters are $0, which
        # disables the increase and preserves the flat $20,000 cap.
        filing_status = person.tax_unit("filing_status", period)
        agi = person.tax_unit("adjusted_gross_income", period)
        agi_limit = where(
            filing_status == filing_status.possible_values.JOINT,
            p.ss_cap_increase_agi_limit.joint,
            p.ss_cap_increase_agi_limit.single,
        )
        qualifies_for_cap_increase = (eligible_taxable_social_security > cap) & (
            agi <= agi_limit
        )
        middle_cap = where(
            qualifies_for_cap_increase, eligible_taxable_social_security, cap
        )
        capped_middle_amount = min_(eligible_taxable_social_security, middle_cap)
        # If the filer is under 55, they can claim a capped amount of ss survivors
        capped_younger_amount = min_(eligible_social_security_survivors, cap)
        return select(
            [
                age >= p.age_threshold.older,
                age >= p.age_threshold.younger,
            ],
            [taxable_social_security, capped_middle_amount],
            default=capped_younger_amount,
        )

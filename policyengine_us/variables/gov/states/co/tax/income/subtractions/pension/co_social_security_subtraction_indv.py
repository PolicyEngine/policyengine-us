from policyengine_us.model_api import *


class co_social_security_subtraction_indv(Variable):
    value_type = float
    entity = Person
    label = "Colorado social security subtraction for eligible individuals"
    defined_for = StateCode.CO
    unit = USD
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12",
        "https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-104/"
        # C.R.S. 39-22-104(4)(g)(III)
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.tax.income.subtractions.pension
        if not p.social_security_subtraction_available:
            return 0
            p = parameters(
                period
            ).gov.states.co.tax.income.subtractions.pension
            taxable_social_security = person("taxable_social_security", period)
            social_security_survivors = person(
                "social_security_survivors", period
            )
            age = person("age", period)
            head = person("is_tax_unit_head", period)
            spouse = person("is_tax_unit_spouse", period)
            head_or_spouse = head | spouse
            age_head_or_spouse = age * head_or_spouse
            younger_condition = age_head_or_spouse < p.age_threshold.younger
            middle_condition = (
                p.age_threshold.older
                > age_head_or_spouse
                >= p.age_threshold.younger
            )
            older_condition = age_head_or_spouse >= p.age_threshold.older
            # Only head and spouse can claim this subtraction
            eligible_social_security_survivors = (
                social_security_survivors * head_or_spouse
            )
            eligible_taxable_social_security = (
                taxable_social_security * head_or_spouse
            )
            # If the filer is 65 or older, they can claim full subtarction
            # If the filer is between 65 and 55, they can claim a capped amount
            cap = p.cap.younger
            capped_middle_amount = min_(eligible_taxable_social_security, cap)
            # If the filer is under 55, they can claim a capped amount of ss survivors
            capped_younger_amount = min_(
                eligible_social_security_survivors, cap
            )
            return select(
                [
                    younger_condition,
                    middle_condition,
                    older_condition,
                ],
                [
                    capped_younger_amount,
                    capped_middle_amount,
                    taxable_social_security,
                ],
            )
        p = parameters(
            period
        ).gov.states.co.tax.income.subtractions.pension
        taxable_social_security = person("taxable_social_security", period)
        social_security_survivors = person(
            "social_security_survivors", period
        )
        age = person("age", period)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = head | spouse
        age_head_or_spouse = age * head_or_spouse
        younger_condition = age_head_or_spouse < p.age_threshold.younger
        middle_condition = (
            p.age_threshold.older
            > age_head_or_spouse
            >= p.age_threshold.younger
        )
        older_condition = age_head_or_spouse >= p.age_threshold.older
        # Only head and spouse can claim this subtraction
        eligible_social_security_survivors = (
            social_security_survivors * head_or_spouse
        )
        eligible_taxable_social_security = (
            taxable_social_security * head_or_spouse
        )
        # If the filer is 65 or older, they can claim full subtarction
        # If the filer is between 65 and 55, they can claim a capped amount
        cap = p.cap.younger
        capped_middle_amount = min_(eligible_taxable_social_security, cap)
        # If the filer is under 55, they can claim a capped amount of ss survivors
        capped_younger_amount = min_(
            eligible_social_security_survivors, cap
        )
        return select(
            [
                younger_condition,
                middle_condition,
                older_condition,
            ],
            [
                capped_younger_amount,
                capped_middle_amount,
                taxable_social_security,
            ],
        )

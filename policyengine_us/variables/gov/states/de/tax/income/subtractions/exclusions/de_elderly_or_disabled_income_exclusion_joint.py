from policyengine_us.model_api import *


class de_elderly_or_disabled_income_exclusion_joint(Variable):
    value_type = float
    entity = Person
    label = "Delaware individual aged or disabled exclusion when married filing jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        # 30 Del. C. § 1106(b)(2)
        "https://delcode.delaware.gov/title30/c011/sc02/index.html#1106",
        "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=7",
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-01_PaperInteractive.pdf#page=1",
    )
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.de.tax.income.subtractions.exclusions.elderly_or_disabled

        # A joint return tests the couple, not each spouse (line 11
        # worksheet): both spouses are 60 or older or totally and
        # permanently disabled, their combined earned income is under
        # $5,000, and the joint return's line 10 is $20,000 or less.
        age_eligible = person("age", period) >= p.eligibility.age_threshold
        age_or_disability_eligible = age_eligible | person("is_disabled", period)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        both_spouses_eligible = tax_unit.any(
            head & age_or_disability_eligible
        ) & tax_unit.any(spouse & age_or_disability_eligible)

        head_or_spouse = head | spouse
        combined_earned_income = tax_unit.sum(
            head_or_spouse * person("earned_income", period)
        )
        earned_income_eligible = (
            combined_earned_income < p.eligibility.earned_income_limit[filing_status]
        )

        # Line 10 of the joint return, as de_agi_joint totals it.
        joint_pre_exclusions_agi = tax_unit.sum(person("de_pre_exclusions_agi", period))
        agi_eligible = joint_pre_exclusions_agi <= p.eligibility.agi_limit[filing_status]

        joint_eligible = (
            head_or_spouse
            & both_spouses_eligible
            & earned_income_eligible
            & agi_eligible
        )

        # Other returns test each filer on their own.
        individual_eligible = person(
            "de_elderly_or_disabled_income_exclusion_eligible_person", period
        )
        joint = filing_status == filing_status.possible_values.JOINT
        eligible = where(joint, joint_eligible, individual_eligible)
        # The JOINT amount is half the $4,000 joint exclusion, for each spouse.
        return p.amount[filing_status] * eligible

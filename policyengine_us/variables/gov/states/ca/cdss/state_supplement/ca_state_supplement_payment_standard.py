from policyengine_us.model_api import *


class ca_state_supplement_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CAPI payment standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.state_supplement.payment_standard
        person = spm_unit.members
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = head | spouse
        # Blind amount
        blind = person("is_blind", period) * head_or_spouse
        blind_count = spm_unit.sum(blind)
        is_married = spm_unit("spm_unit_is_married", period)
        blind_married_amount = select(
            [blind_count >= 2, blind_count == 1],
            [p.blind.married.two_blind, p.blind.married.one_blind],
            default=0,
        )
        blind_amount = where(is_married, blind_married_amount, p.blind.single)
        # Aged or disabled amount
        is_disabled = person("is_disabled", period)
        age = person("monthly_age", period)
        is_aged = age >= p.aged_or_disabled.age_threshold
        aged_or_disabled = (is_aged | is_disabled) * head_or_spouse
        aged_disabled_count = spm_unit.sum(aged_or_disabled)
        aged_disabled_amount = select(
            [
                (aged_disabled_count >= 2) & (is_married == 1),
                aged_disabled_count == 1,
            ],
            [
                p.aged_or_disabled.amount.married,
                p.aged_or_disabled.amount.single,
            ],
            default=0,
        )
        # Food allowance amount
        living_arrangements_allow_for_food_preparation = spm_unit.household(
            "living_arrangements_allow_for_food_preparation", period
        )
        food_allowance_amount = select(
            [
                (is_married == 1) & (aged_disabled_count == 2),
                (is_married == 1) & (aged_disabled_count == 1),
                (aged_disabled_count == 1),
            ],
            [
                p.allowance.food.married,
                p.allowance.food.single,
                p.allowance.food.single,
            ],
            default=0,
        )
        food_allowance_full_amount = (
            living_arrangements_allow_for_food_preparation
            * food_allowance_amount
        )
        # Dependent amount
        dependent = person("is_tax_unit_dependent", period)
        dependent_age_eligible = age < p.dependent.age_limit
        dependent_count = spm_unit.sum(
            dependent & dependent_age_eligible & (is_disabled | blind)
        )
        dependent_amount = dependent_count * p.dependent.amount
        # Medical care facility amount
        is_in_medical_care_facility = person(
            "ca_in_medical_care_facility", period
        )
        medical_care_facility_count = spm_unit.sum(is_in_medical_care_facility)
        medical_care_facility_amount = (
            medical_care_facility_count * p.allowance.medical_care_facility
        )
        # Out of home care facility amount
        is_in_out_of_home_care_facility = person(
            "ca_in_out_of_home_care_facility", period
        )
        out_of_home_care_facility_count = spm_unit.sum(
            is_in_out_of_home_care_facility
        )
        out_of_home_care_facility_amount = (
            out_of_home_care_facility_count * p.allowance.out_of_home_care
        )
        # Total amount
        return (
            max_(blind_amount, aged_disabled_amount)
            + food_allowance_full_amount
            + dependent_amount
            + medical_care_facility_amount
            + out_of_home_care_facility_amount
        )

from policyengine_us.model_api import *


class va_subtractions_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia adjusted gross income subtractions attributed to each person"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(person, period, parameters):
        # Virginia's "Worksheet for Determining Separate Virginia Adjusted Gross
        # Income" (Form 760 instructions, STEP 2, Lines 14-17) attributes each
        # subtraction to the spouse who received the underlying income. This
        # builds each person's share so the per-person amounts sum to the tax
        # unit's va_subtractions, which matters for the Spouse Tax Adjustment and
        # the per-person Virginia EITC split.
        #
        # The components below mirror, item by item, the subtractions listed in
        # gov.states.va.tax.income.subtractions.subtractions; keep them in sync.
        tax_unit = person.tax_unit
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        p = parameters(period).gov.states.va.tax.income.subtractions

        # Person-level income exclusions: the income (and therefore the
        # subtraction) belongs to the individual who received it.
        age_deduction = person("va_age_deduction_person", period)  # Line 14
        social_security = person("taxable_social_security", period)  # Line 15
        railroad = person("railroad_benefits", period)  # Line 15 (Tier 1 Railroad)
        unemployment = person("unemployment_compensation", period)  # Line 17
        us_govt_interest = person("us_govt_interest_person", period)  # Line 17

        # Military basic pay subtraction: phases in then out per person (mirrors
        # va_military_basic_pay_subtraction).
        military_pay = person("military_basic_pay", period)
        military_basic_pay_subtraction = (
            where(
                military_pay < p.military_basic_pay.threshold,
                military_pay,
                max_(0, 2 * p.military_basic_pay.threshold - military_pay),
            )
            * is_head_or_spouse
        )
        # Disability income subtraction, capped per person (mirrors
        # va_disability_income_subtraction).
        disability = (
            min_(person("disability_benefits", period), p.disability_income.amount)
            * is_head_or_spouse
        )
        # Federal/state employees subtraction (mirrors
        # va_federal_state_employees_subtraction, which gates on the disability
        # income amount parameter).
        employment_income = person("irs_employment_income", period)
        federal_state_employees = (
            where(
                employment_income > p.disability_income.amount,
                0,
                person("state_or_federal_salary", period),
            )
            * is_head_or_spouse
        )
        # Military benefit subtraction, capped and optionally age-gated (mirrors
        # va_military_benefit_subtraction).
        military_benefit = min_(
            person("military_retirement_pay", period), p.military_benefit.amount
        )
        if p.military_benefit.availability:
            military_benefit = military_benefit * (
                person("age", period) >= p.military_benefit.age_threshold
            )
        military_benefit = military_benefit * is_head_or_spouse

        # National Guard subtraction caps the sum of military service income, so
        # allocate the (capped) tax-unit amount by each person's share.
        national_guard_total = tax_unit("va_national_guard_subtraction", period)
        military_service_income = person("military_service_income", period)
        total_military_service_income = tax_unit.sum(military_service_income)
        national_guard_share = where(
            total_military_service_income > 0,
            military_service_income / total_military_service_income,
            0,
        )
        national_guard = national_guard_total * national_guard_share

        # The 529 deduction is a household contribution, not a person's income,
        # so it cannot make a spouse's separate VAGI exceed their own income;
        # prorate it by federal AGI share.
        plan_529_total = tax_unit("va_529_plan_deduction", period)
        person_fagi = person("adjusted_gross_income_person", period)
        total_federal_agi = tax_unit.sum(person_fagi)
        federal_agi_share = where(
            total_federal_agi > 0, person_fagi / total_federal_agi, 0
        )
        plan_529 = plan_529_total * federal_agi_share

        return (
            age_deduction
            + social_security
            + railroad
            + unemployment
            + us_govt_interest
            + military_basic_pay_subtraction
            + disability
            + federal_state_employees
            + military_benefit
            + national_guard
            + plan_529
        )

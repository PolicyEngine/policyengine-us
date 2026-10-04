from policyengine_us.model_api import *


class de_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Delaware LIHEAP adjusted annual countable income"
    defined_for = StateCode.DE
    reference = "https://liheapch.acf.gov/docs/2026/state-plans/DE_Plan_2026.pdf#page=5"

    def formula(spm_unit, period, parameters):
        # Keep income of members excluded from qualified household size.
        # Annual flows approximate the application's assessment period.
        income = add(spm_unit, period, ["de_liheap_countable_income_person", "de_tanf"])
        # This existing annual tax estimate approximates payroll withholding;
        # it does not observe actual withheld tax. It already includes the DE
        # employee paid-leave contribution through employee_payroll_tax.
        person = spm_unit.members
        p = parameters(period).gov.states.de.dhss.liheap.income
        age = person("age", period)
        student_exempt = (
            person("is_full_time_college_student", period)
            & person("is_tax_unit_dependent", period)
            & (age < p.student_income_exclusion_age)
        )
        excluded_earner = (age < p.earned_income_min_age) | student_exempt
        payroll_tax = add(
            person,
            period,
            [
                "employee_social_security_tax",
                "employee_medicare_tax",
                "de_employee_state_payroll_tax",
            ],
        )
        # DE withholding is a Person estimate. Remove the excluded earnings'
        # contribution to its AGI base, preserving tax on counted unearned
        # income. IRS wages already exclude pre-tax payroll contributions.
        taxable_earned = sum(
            max_(
                person(
                    "irs_employment_income"
                    if source == "employment_income"
                    else source,
                    period,
                ),
                0,
            )
            for source in p.sources.earned
        )
        business_adjustments = add(
            person,
            period,
            [
                "self_employment_tax_ald_person",
                "self_employed_health_insurance_ald_person",
                "self_employed_pension_contribution_ald_person",
            ],
        )
        earned_agi = where(
            person("is_tax_unit_dependent", period),
            0,
            max_(taxable_earned - business_adjustments, 0),
        )
        remaining_agi = where(
            student_exempt,
            0,
            person("adjusted_gross_income_person", period) - earned_agi,
        )
        state_tax = parameters(period).gov.states.de.tax.income
        remaining_state_tax = state_tax.rate.calc(
            max_(remaining_agi - state_tax.deductions.standard.amount["SINGLE"], 0)
        )
        excluded_state_tax = where(
            excluded_earner,
            max_(person("de_withheld_income_tax", period) - remaining_state_tax, 0),
            0,
        )
        # Remove identifiable taxes on excluded earnings from the supplied
        # aggregate; keep any remaining deduction and never create a refund.
        withholding = max_(
            spm_unit("spm_unit_paycheck_withholdings", period)
            - spm_unit.sum(where(excluded_earner, payroll_tax, 0) + excluded_state_tax),
            0,
        )
        city_earnings = where(
            person.household("in_wilmington", period),
            person("employment_income", period)
            + person("self_employment_income", period),
            person("de_wilmington_nonresident_earnings", period),
        )
        city_rate = parameters(period).gov.local.de.wilmington.tax.income.rate
        city_tax = max_(
            add(spm_unit, period, ["de_wilmington_earned_income_tax"])
            - spm_unit.sum(where(excluded_earner, max_(city_earnings, 0), 0))
            * city_rate,
            0,
        )
        # Federal income tax and additional Medicare are TaxUnit aggregates
        # without a person allocation; retain that annual-estimate limitation.
        # TANF is a household amount with no person-level student allocation.
        return max_(income - withholding - city_tax, 0)

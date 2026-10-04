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
        excluded_earner = (age < p.earned_income_min_age) | (
            person("is_full_time_college_student", period)
            & person("is_tax_unit_dependent", period)
            & (age < p.student_income_exclusion_age)
        )
        payroll_tax = add(
            person,
            period,
            [
                "employee_social_security_tax",
                "employee_medicare_tax",
                "de_employee_state_payroll_tax",
            ],
        )
        # Remove identifiable taxes on excluded earnings from the supplied
        # aggregate; keep any remaining deduction and never create a refund.
        withholding = max_(
            spm_unit("spm_unit_paycheck_withholdings", period)
            - spm_unit.sum(where(excluded_earner, payroll_tax, 0)),
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

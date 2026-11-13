from policyengine_us.model_api import *


class ma_qualified_unemployment_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Massachusetts qualified unemployment deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://malegislature.gov/Laws/SessionLaws/Acts/2021/Chapter9",
        "https://taxsim.nber.org/historical_state_tax_forms/MA/2021/dor-2021-inc-form-1-inst.pdf#page=21",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.tax.income.deductions.qualified_unemployment
        if not p.in_effect:
            return 0
        # Worksheet lines 1-4: household size is 2 if married filing jointly,
        # otherwise 1, plus dependents.
        size = (
            1
            + tax_unit("tax_unit_is_joint", period)
            + tax_unit("tax_unit_dependents", period)
        )
        limit = p.income_limit.base + (size - 1) * p.income_limit.additional_person
        # Filers enter their Form 1040 lines 11, 2a, 6a and 6b on worksheet
        # lines 5-7. Filers exclude dependents' own interest and benefits.
        untaxed_social_security = tax_unit(
            "tax_unit_social_security_for_taxability", period
        ) - tax_unit("tax_unit_taxable_social_security", period)
        household_income = (
            tax_unit("adjusted_gross_income", period)
            + tax_unit_non_dep_add(tax_unit, period, ["tax_exempt_interest_income"])
            + untaxed_social_security
        )
        # Lines 10-14: up to the cap for each of the filer and spouse.
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        capped = min_(person("taxable_unemployment_compensation", period), p.cap)
        deduction = tax_unit.sum(capped * head_or_spouse)
        return where(household_income <= limit, deduction, 0)

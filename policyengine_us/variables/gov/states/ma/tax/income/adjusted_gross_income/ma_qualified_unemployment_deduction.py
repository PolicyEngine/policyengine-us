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
        # otherwise 1, plus the number of dependents claimed, which is none on
        # a return with a filer whom another taxpayer can claim (IRC
        # 152(b)(1)).
        dependents = where(
            tax_unit("head_or_spouse_is_dependent_elsewhere", period),
            0,
            tax_unit("tax_unit_dependents", period),
        )
        size = 1 + tax_unit("tax_unit_is_joint", period) + dependents
        limit = p.income_limit.base + (size - 1) * p.income_limit.additional_person
        # Lines 5-9: federal AGI + tax-exempt interest + untaxed social security.
        untaxed_social_security = tax_unit(
            "tax_unit_social_security", period
        ) - tax_unit("tax_unit_taxable_social_security", period)
        household_income = (
            tax_unit("adjusted_gross_income", period)
            + add(tax_unit, period, ["tax_exempt_interest_income"])
            + untaxed_social_security
        )
        # Lines 10-14: up to the cap for each of the filer and spouse.
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        capped = min_(person("taxable_unemployment_compensation", period), p.cap)
        deduction = tax_unit.sum(capped * head_or_spouse)
        return where(household_income <= limit, deduction, 0)

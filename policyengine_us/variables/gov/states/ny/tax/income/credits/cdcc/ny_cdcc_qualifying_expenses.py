from policyengine_us.model_api import *


class ny_cdcc_qualifying_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York child and dependent care credit qualifying expenses"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-2)(2)(C), (D)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.cdcc.decoupled
        # (D)(i) care for qualifying individuals; childcare_expenses already
        # nets out government child care subsidies. (D)(ii)(a) excludes amounts
        # paid from a dependent care account.
        care = tax_unit("tax_unit_childcare_expenses", period) + add(
            tax_unit, period, ["care_expenses"]
        )
        account = add(tax_unit, period, ["dependent_care_employer_benefits"])
        expenses = max_(care - account, 0)
        # (D)(iii) caps expenses by the number of qualifying individuals and at
        # earned income, the lesser of each spouse's on a joint return. Unlike
        # IRC 21(d)(2), 606(c-2) deems no earned income for a student or
        # incapacitated spouse.
        cap = p.expense_cap.calc(tax_unit("count_cdcc_eligible", period))
        # (C) defines earned income as "the wages, salaries, tips and other
        # employee compensation", without IRC 32(c)(2)(A)(i)'s "only if such
        # amounts are includible in gross income". head_earned and
        # spouse_earned follow 32(c)(2), so add back the pre-tax payroll
        # deductions they leave out.
        person = tax_unit.members
        excluded_wages = person("employment_income", period) - person(
            "irs_employment_income", period
        )
        head_earned = tax_unit("head_earned", period) + tax_unit.sum(
            excluded_wages * person("is_tax_unit_head", period)
        )
        spouse_earned = tax_unit("spouse_earned", period) + tax_unit.sum(
            excluded_wages * person("is_tax_unit_spouse", period)
        )
        earned = where(
            tax_unit("tax_unit_is_joint", period),
            min_(head_earned, spouse_earned),
            head_earned,
        )
        return min_(expenses, min_(cap, earned))

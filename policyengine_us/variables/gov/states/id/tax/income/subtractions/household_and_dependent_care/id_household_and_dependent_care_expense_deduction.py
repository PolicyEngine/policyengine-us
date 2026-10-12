from policyengine_us.model_api import *


class id_household_and_dependent_care_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho household and dependent care expense deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.id.tax.income.deductions.dependent_care_expenses
        # Idaho Code §63-3022D adopts the IRC §21(b)(2) employment-related
        # expense definition, which covers childcare plus care for a disabled
        # adult qualifying individual (care_expenses).
        childcare = tax_unit("tax_unit_childcare_expenses", period)
        adult_care = add(tax_unit, period, ["care_expenses"])
        expenses = childcare + adult_care
        # In 2023 Idaho implemented an increased cap independent of the number of children
        limit = max_(tax_unit("id_cdcc_limit", period), p.cap)
        # Form 39R Line 6 worksheet line 4: the operative cap is reduced by the
        # IRC § 129 employer-provided dependent care benefits ("excluded
        # benefits from Part III of Form 2441"), mirroring the § 21(c) reduction
        # the federal credit's base applies.
        exclusion = tax_unit("dependent_care_assistance_exclusion", period)
        limit = max_(limit - exclusion, 0)
        eligible_capped_expenses = min_(expenses, limit)
        # cap further to the lowest earnings between the taxpayer and spouse
        return min_(
            eligible_capped_expenses,
            tax_unit("min_head_spouse_earned", period),
        )

from policyengine_us.model_api import *


class hi_min_head_spouse_earned(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii minimum income between head and spouse"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=28"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.cdcc
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        # earned minimum income if is disabled/full-time student
        head_eligible = head & (
            person("is_disabled", period)
            | person("is_full_time_student", period)
        )
        spouse_eligible = spouse & (
            person("is_disabled", period)
            | person("is_full_time_student", period)
        )
        # 2400 --> one dependent, 4800 --> more than one dependent
        qualified_children = tax_unit("count_cdcc_eligible", period)
        income = person("earned_income", period)
        head_income = where(
            sum(head_eligible) != 0,
            where(
                qualified_children <= 1,
                max_(
                    p.expense_cap.one_child,
                    tax_unit.sum(head * income),
                ),
                max_(
                    p.expense_cap.two_or_more_child,
                    tax_unit.sum(head * income),
                ),
            ),
            tax_unit.sum(head * income),
        )
        spouse_income = where(
            sum(spouse) != 0,
            where(
                sum(spouse_eligible) != 0,
                where(
                    qualified_children <= 1,
                    max_(
                        p.expense_cap.one_child,
                        tax_unit.sum(spouse * income),
                    ),
                    max_(
                        p.expense_cap.two_or_more_child,
                        tax_unit.sum(spouse * income),
                    ),
                ),
                tax_unit.sum(spouse * income),
            ),
            head_income,
        )

        return min_(head_income, spouse_income)

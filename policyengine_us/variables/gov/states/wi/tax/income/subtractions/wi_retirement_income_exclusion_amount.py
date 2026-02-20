from policyengine_us.model_api import *


class wi_retirement_income_exclusion_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin retirement income exclusion amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m/a",
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleSB-Inst.pdf#page=7",
    )
    defined_for = "wi_retirement_income_exclusion_eligible"

    def formula(tax_unit, period, parameters):
        # Schedule SB Line 16: qualifying retirement income, capped.
        # This is NOT subtracted from income directly — instead it
        # feeds into wi_retirement_income_exclusion_tax_reduction,
        # which compares tax computed two ways (with vs without the
        # exclusion) because claiming Line 16 forfeits all credits.
        p = parameters(
            period
        ).gov.states.wi.tax.income.subtractions.retirement_income.exclusion
        person = tax_unit.members
        age = person("age", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        eligible = (age >= p.min_age) * head_or_spouse
        pension = person("taxable_pension_income", period)
        ira = person("taxable_ira_distributions", period)
        person_ret_income = (pension + ira) * eligible

        filing_status = tax_unit("filing_status", period)
        is_joint = filing_status == filing_status.possible_values.JOINT
        both_eligible = tax_unit.sum(eligible) >= 2

        total_ret_income = tax_unit.sum(person_ret_income)

        # Joint with both 67+: pool and cap at joint max
        joint_both_amount = min_(p.max_amount.joint, total_ret_income)

        # Otherwise: per-person cap at single max, sum to tax unit
        per_person_capped = min_(p.max_amount.single, person_ret_income)
        standard_amount = tax_unit.sum(per_person_capped)

        return where(
            is_joint & both_eligible,
            joint_both_amount,
            standard_amount,
        )

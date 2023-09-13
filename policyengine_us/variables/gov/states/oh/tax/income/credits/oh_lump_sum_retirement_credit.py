from policyengine_us.model_api import *


class oh_lump_sum_retirement_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Lump Sum Retirement Income Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.055"  # (C, D, E)
    defined_for = "oh_retirement_income_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.credits

        person = tax_unit.members
        is_spouse = person("is_tax_unit_spouse", period)
        is_head = person("is_tax_unit_head", period)

        pension_income = person("pension_income", period)
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        head_eligible = where(
            age_head >= p.lump_sum_retirement.age_threshold, 1, 0
        )
        spouse_eligible = where(
            age_spouse >= p.lump_sum_retirement.age_threshold, 1, 0
        )

        head_divisor = p.lump_sum_retirement.multiple.calc(age_head)
        spouse_divisor = p.lump_sum_retirement.multiple.calc(age_spouse)

        head_pension = tax_unit.sum(is_head * pension_income)
        spouse_pension = tax_unit.sum(is_spouse * pension_income)

        head_credit = where(
            head_divisor == 0,
            0,
            p.retirement_income.amount.calc(
                head_pension / head_divisor, right=True
            )
            * head_divisor,
        )
        spouse_credit = where(
            spouse_divisor == 0,
            0,
            p.retirement_income.amount.calc(
                spouse_pension / spouse_divisor, right=True
            )
            * spouse_divisor,
        )

        # distribution_received = tax_unit("c05700", period) > 0 # received lump sum distribution
        distribution_received = (
            tax_unit("form_4972_lumpsum_distributions", period) > 0
        )

        return np.where(
            distribution_received,
            head_credit * head_eligible + spouse_credit * spouse_eligible,
            0,
        )

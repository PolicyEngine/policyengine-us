from policyengine_us.model_api import *


class in_unified_elderly_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana unified elderly tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://iga.in.gov/laws/2021/ic/titles/6#6-3-3-9"
        "https://iga.in.gov/laws/2022/ic/titles/6#6-3-3-9"
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.states["in"].tax.income.credits
        head_age = tax_unit("age_head", period)
        aged_head = (head_age >= p.unified_elderly.min_age).astype(int)
        spouse_age = tax_unit("age_spouse", period)
        aged_spouse = (spouse_age >= p.unified_elderly.min_age).astype(int)
        aged_count = aged_head + aged_spouse
        return select(
            [
                aged_count == 1,
                aged_count == 2,
            ],
            [
                p.unified_elderly.amount.one_aged.calc(federal_agi),
                p.unified_elderly.amount.two_aged.calc(federal_agi),
            ],
            default=0,
        )

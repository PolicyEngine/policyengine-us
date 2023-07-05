from policyengine_us.model_api import *


class in_unified_elderly_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana unified elderly tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://forms.in.gov/Download.aspx?id=15394"
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = (
            parameters(period)
            .gov.states["in"]
            .tax.income.credits.unified_elderly
        )
        income = person("in_unified_elderly_tax_income", period)
        total_income = tax_unit.sum(income)
        age_head = tax_unit("age_head", period)
        spouse_age = tax_unit("age_spouse", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        married = status.JOINT
        head_eligible = age_head >= p.age_eligibility
        spouse_eligible = spouse_age >= p.age_eligibility
        both_eligible = head_eligible & spouse_eligible
        eligible = head_eligible | spouse_eligible
        married_amount = where(
            both_eligible,
            p.amount.married.two_aged.calc(total_income),
            p.amount.married.one_aged.calc(total_income),
        )
        single_amount = p.amount.single.calc(total_income) * head_eligible
        return eligible * where(married, married_amount, single_amount)

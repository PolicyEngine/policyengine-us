from policyengine_us.model_api import *


class sc_two_wage_earner_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina two wage earner credit"
    defined_for = StateCode.SC
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/forms-site/Forms/SC1040TT_2021.pdf",
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=23",
    )

    def formula(tax_unit, period, parameters):
        # Determine eligibility. Must be a joint filer.
        filing_status = tax_unit("filing_status", period)
        eligible = filing_status == filing_status.possible_values.JOINT
        # Find relevant gross income of head and spouse.
        person = tax_unit.members
        income = person("sc_gross_earned_income", period)
        head_income = tax_unit.max(income * person("is_tax_unit_head", period))
        spouse_income = tax_unit.max(
            income * person("is_tax_unit_spouse", period)
        )
        # Determine lesser of head and spouse income.
        lesser_head_spouse_income = min_(head_income, spouse_income)
        # Calculate credit based on rate.
        p = parameters(period).gov.states.sc.tax.income.credits.two_wage_earner
        credit_if_eligible = p.rate.calc(lesser_head_spouse_income)
        return credit_if_eligible * eligible

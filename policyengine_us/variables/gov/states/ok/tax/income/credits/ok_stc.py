from policyengine_us.model_api import *


class ok_stc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma sales tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        # for details, see Form 538-S in the 511 packets referenced above
        p = parameters(period).gov.states.ok.tax.income.credits.sales_tax
        # determine TANF ineligibility
        tanf_ineligible = add(tax_unit, period, ["ok_tanf"]) > 0
        # determine income eligibility in two alternative ways
        income = tax_unit("ok_gross_income", period)
        # ... first way
        income_eligible1 = income <= p.income_limit1
        # ... second way
        count_dependents = tax_unit("tax_unit_dependents", period)
        has_dependents = count_dependents > 0
        elderly_head = tax_unit("age_head", period) >= p.age_minimum
        elderly_spouse = tax_unit("age_spouse", period) >= p.age_minimum
        has_elder = elderly_head | elderly_spouse
        disabled_head = tax_unit("head_is_disabled", period)
        disabled_spouse = tax_unit("spouse_is_disabled", period)
        has_disabled = disabled_head | disabled_spouse
        unit_eligible = has_dependents | has_elder | has_disabled
        income_eligible2 = unit_eligible & (income <= p.income_limit2)
        # determine overall eligibility
        eligible = ~tanf_ineligible & (income_eligible1 | income_eligible2)
        # calculate credit if eligible
        qualified_exemptions = tax_unit("num", period) + count_dependents
        return eligible * qualified_exemptions * p.amount

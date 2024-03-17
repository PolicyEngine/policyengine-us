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
        has_dependents = tax_unit("tax_unit_dependents", period) > 0
        elderly_head_or_spouse = (
            tax_unit("greater_age_head_spouse", period) >= p.age_minimum
        )
        disabled_head_or_spouse = tax_unit(
            "disabled_tax_unit_head_or_spouse", period
        )
        unit_eligible = (
            has_dependents | elderly_head_or_spouse | disabled_head_or_spouse
        )
        income_eligible2 = unit_eligible & (income <= p.income_limit2)
        # determine overall eligibility
        eligible = ~tanf_ineligible & (income_eligible1 | income_eligible2)
        # calculate credit if eligible
        qualified_exemptions = tax_unit("tax_unit_size", period)
        return eligible * qualified_exemptions * p.amount

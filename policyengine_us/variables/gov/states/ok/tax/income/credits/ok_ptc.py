from policyengine_us.model_api import *


class ok_ptc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/538-H-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-H.pdf"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ok.tax.income.credits.property_tax
        # determine eligibility
        elderly_head = tax_unit("age_head", period) >= p.age_minimum
        elderly_spouse = tax_unit("age_spouse", period) >= p.age_minimum
        disabled_head = tax_unit("head_is_disabled", period)
        unit_eligible = elderly_head | elderly_spouse | disabled_head
        income = tax_unit("ok_gross_income", period)
        income_eligible = income <= p.income_limit
        eligible = unit_eligible & income_eligible
        # calculate credit if eligible
        tax = add(tax_unit, period, ["real_estate_taxes"])
        excess_property_tax = max_(0, tax - p.income_fraction * income)
        return eligible * min_(p.maximum_credit, excess_property_tax)

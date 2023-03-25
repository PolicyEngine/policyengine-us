from policyengine_us.model_api import *


class ok_stc(Variable):
    value_type = float
    entity = TaxUnit
    label = "OK sales tax credit"
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
        person = tax_unit.members
        # determine TANF ineligibility
        tanf_ineligible = add(tax_unit, period, ["ok_tanf"]) > 0
        # compute comprehensive income for all people in tax unit
        income = 0
        for source in p.income_sources:
            # income includes only positive amounts (i.e., no losses)
            income += max_(0, add(person, period, [source]))
        income += tax_unit("earned_income_tax_credit", period)
        income += tax_unit("ok_eitc", period)
        # determine income eligibility in one of two alternative ways
        # ... first way
        income_eligible1 = income <= p.income_limit1
        # ... second way
        num_dependents = tax_unit("tax_unit_dependents", period)
        has_dependents = num_dependents > 0
        elderly_head = tax_unit("age_head", period) >= p.age_minimum
        elderly_spouse = tax_unit("age_spouse", period) >= p.age_minimum
        elderly = elderly_head | elderly_spouse
        disabled_head = tax_unit("head_is_disabled", period)
        disabled_spouse = tax_unit("spouse_is_disabled", period)
        disabled = disabled_head | disabled_spouse
        unit_eligible = has_dependents | elderly | disabled
        income_eligible2 = unit_eligible & (income <= p.income_limit2)
        income_eligible = income_eligible1 | income_eligible2
        # determine overall eligibility
        eligible = ~tanf_ineligible & income_eligible
        # calculate credit if eligible
        qualified_exemptions = tax_unit("num", period) + num_dependents
        return eligible * qualified_exemptions * p.amount

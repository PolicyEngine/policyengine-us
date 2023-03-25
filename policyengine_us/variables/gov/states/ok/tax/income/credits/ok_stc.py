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
        # compute comprehensive gross income for all people in tax unit
        tax_unit_income_sources = [
            "earned_income_tax_credit",
            "ok_eitc",
        ]
        person_income_sources = [
            source
            for source in p.income_sources
            if source not in tax_unit_income_sources
        ]
        income = 0
        for source in person_income_sources:
            # income includes only positive amounts (i.e., no losses)
            income += max_(0, add(person, period, [source]))
        income += add(tax_unit, period, tax_unit_income_sources)
        # determine income eligibility in two alternative ways
        # ... first way
        income_eligible1 = income <= p.income_limit1
        # ... second way
        num_dependents = tax_unit("tax_unit_dependents", period)
        has_dependents = num_dependents > 0
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
        qualified_exemptions = tax_unit("num", period) + num_dependents
        return eligible * qualified_exemptions * p.amount

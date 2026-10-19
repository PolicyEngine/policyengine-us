from policyengine_us.model_api import *


class va_personal_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia personal exemption for each person"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"

    def formula(person, period, parameters):
        # Va. Code 58.1-322.03(2)(a) allows $930 for "each personal exemption
        # allowable to the taxpayer for federal income tax purposes". A filer
        # whom another taxpayer can claim has none (IRC 151(d)(2)), and a
        # return on which the filer (or, if joint, either spouse) can be
        # claimed has no dependents (IRC 152(b)(1); the 760 instructions
        # allow "the same number of dependent exemptions allowed on your
        # federal return").
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed = person("claimable_as_dependent_on_another_return", period)
        dependent = person("is_tax_unit_dependent", period)
        dependent_filer = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        eligible = (filer & ~claimed) | (dependent & ~dependent_filer)
        p = parameters(period).gov.states.va.tax.income.exemptions
        return eligible * p.personal

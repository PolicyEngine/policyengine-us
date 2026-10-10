from policyengine_us.model_api import *


class va_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia standard deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.deductions
        filing_status = tax_unit("filing_status", period)
        standard = p.standard[filing_status]
        # Va. Code 58.1-322.03(1)(b): for an individual who can be claimed as
        # a dependent on another taxpayer's return the standard deduction is
        # computed "only with respect to earned income" (Form 760 instructions:
        # "limited to the amount of your earned income"), with no federal
        # floor or add-on. Virginia taxes a joint return on one joint taxable
        # income (58.1-324(B)(1)), so either spouse being claimable caps the
        # joint deduction at the couple's earned income.
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        filer_earned_income = tax_unit.sum(
            filer * max_(person("earned_income", period), 0)
        )
        dependent_filer = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        return where(dependent_filer, min_(standard, filer_earned_income), standard)

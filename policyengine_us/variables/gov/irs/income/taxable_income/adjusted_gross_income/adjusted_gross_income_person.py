from policyengine_us.model_api import *


class adjusted_gross_income_person(Variable):
    value_type = float
    entity = Person
    label = "Federal adjusted gross income for each person"
    unit = USD
    documentation = (
        "Each person's part of the tax unit's federal AGI: their own gross "
        "income less their own above-the-line deductions "
        "(above_the_line_deductions_person). On a joint return a deduction "
        "that belongs to one spouse, such as their IRA deduction, lowers only "
        "that spouse's AGI. The head's and spouse's amounts add up to the tax "
        "unit's adjusted_gross_income. A tax unit dependent's income and "
        "deductions are on their own return, so their amount here is zero."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/62"

    def formula(person, period, parameters):
        gross_income = person("irs_gross_income", period)
        # A tax unit dependent's deductions are on their own return, as
        # irs_gross_income leaves their income off this one.
        not_dependent = ~person("is_tax_unit_dependent", period)
        deductions = person("above_the_line_deductions_person", period)
        agi = gross_income - not_dependent * deductions
        if parameters(period).gov.contrib.ubi_center.basic_income.taxable:
            basic_income = person.tax_unit("basic_income", period)
            # split basic income evenly between head and spouse
            is_head = person("is_tax_unit_head", period)
            is_spouse = person("is_tax_unit_spouse", period)
            fstatus = person.tax_unit("filing_status", period)
            frac = where(fstatus == fstatus.possible_values.JOINT, 0.5, 1.0)
            basic_income_shared = (is_head | is_spouse) * basic_income * frac
            agi += basic_income_shared
        return agi

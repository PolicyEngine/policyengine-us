from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.irs_gross_income.social_security.dependent_taxable_ss_magi import (
    dependent_income_and_deductions,
)


class dependent_taxable_uc_agi(Variable):
    value_type = float
    entity = Person
    label = (
        "Dependent's adjusted gross income for the unemployment compensation exclusion"
    )
    unit = USD
    documentation = """
    The adjusted gross income of IRC 85(c)(2), figured on a dependent's own
    return: adjusted gross income after taxable Social Security and the
    dependent's own above-the-line deductions, without any unemployment
    compensation. It is taxable_uc_agi for a dependent, whose income
    irs_gross_income leaves off the tax unit's return.
    """
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/85#c_2",
        # 2020 Instructions for Form 1040 (rev. 4-2021), Unemployment
        # Compensation Exclusion Worksheet, lines 1 through 6.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2020.pdf#page=88",
    )

    def formula(person, period, parameters):
        # The dependent's own income, with unemployment compensation in full
        # and without Social Security, and their own above-the-line
        # deductions. Of the deductions that list leaves out (IRC 86(b)(2)),
        # IRC 85(c)(2)(A) applies sections 135, 137 and 221, but none of them
        # is the dependent's: the model records the section 135 and 137
        # exclusions for the filer (gov.irs.ald.filer_amounts_recorded_on_
        # dependents), and IRC 221(c) denies a dependent the student loan
        # interest deduction.
        income, deductions = dependent_income_and_deductions(person, period, parameters)
        # IRC 85(c)(2)(B): without regard to section 85, so without the
        # compensation (worksheet line 2 leaves out Schedule 1, line 7).
        income -= max_(0, person("total_unemployment_compensation", period))
        # IRC 85(c)(2)(A): after section 86 (worksheet line 1 includes Form
        # 1040, line 6b).
        income += person("dependent_taxable_social_security", period)
        return income - add(person, period, deductions)

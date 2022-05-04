from openfisca_us.model_api import *


class taxable_ss_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Modified adjusted gross income (SS)"
    unit = USD
    documentation = "Income used to determine taxability of social security."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/86"

    def formula(tax_unit, period, parameters):
        irs = parameters(period).irs
        gross_income_sources = irs.gross_income.sources
        ss_magi = irs.social_security.taxability.income
        ignored_sources = ss_magi.ignored_sources
        income_sources_without_ss = [
            income_source for income_source in gross_income_sources 
            if income_source not in ignored_sources
        ]
        gross_income = add(tax_unit, period, income_sources_without_ss)
        above_the_line_deductions = irs.ald.deductions
        revoked_deductions =ss_magi.revoked_deductions
        deductions = [
            deduction for deduction in above_the_line_deductions
            if deduction not in revoked_deductions
        ]
        total_deductions = add(tax_unit, period, deductions)
        return max_(0, gross_income - total_deductions)
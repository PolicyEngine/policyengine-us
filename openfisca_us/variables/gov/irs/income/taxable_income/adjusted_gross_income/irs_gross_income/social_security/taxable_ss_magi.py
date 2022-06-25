from openfisca_us.model_api import *


class taxable_ss_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Modified adjusted gross income (SS)"
    unit = USD
    documentation = "Income used to determine taxability of Social Security."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/86"

    def formula(tax_unit, period, parameters):
        irs = parameters(period).gov.irs
        gross_income_sources = irs.gross_income.sources
        ss_magi = irs.social_security.taxability.income
        income_sources_without_ss = [
            income_source
            for income_source in gross_income_sources
            if income_source
            not in [
                "taxable_social_security",
                "taxable_unemployment_compensation",
            ]
        ]
        if "taxable_unemployment_compensation" in gross_income_sources:
            # Reforms which drop the UI variable from gross income should
            # trigger SS-related MAGI to drop it too.
            income_sources_without_ss.append("unemployment_compensation")
        gross_income = 0
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        for source in income_sources_without_ss:
            # Add positive values only - losses are deducted later.
            gross_income += not_dependent * max_(
                0, add(person, period, [source])
            )
        gross_income = tax_unit.sum(gross_income)
        above_the_line_deductions = irs.ald.deductions
        revoked_deductions = ss_magi.revoked_deductions
        deductions = [
            deduction
            for deduction in above_the_line_deductions
            if deduction not in revoked_deductions
        ]
        total_deductions = add(tax_unit, period, deductions)
        return max_(0, gross_income - total_deductions)

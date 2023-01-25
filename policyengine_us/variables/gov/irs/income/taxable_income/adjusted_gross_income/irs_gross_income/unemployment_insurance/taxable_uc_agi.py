from policyengine_us.model_api import *


class taxable_uc_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable unemployment compensation for SS adjusted gross income"
    unit = USD
    documentation = (
        "Income used to determine taxability of unemployment compensation."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/85"

    def formula(tax_unit, period, parameters):
        irs = parameters(period).gov.irs
        gross_income_sources = irs.gross_income.sources
        income_sources_without_ss = [
            income_source
            for income_source in gross_income_sources
            if income_source != "taxable_unemployment_compensation"
        ]
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
        total_deductions = add(tax_unit, period, above_the_line_deductions)
        return max_(0, gross_income - total_deductions)

from policyengine_us.model_api import *


class nj_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=45"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.credits.ctc

        # Get amount per qualifying child based on taxable income.
        taxable_income = tax_unit("nj_taxable_income", period)
        amount_per_qualifying_child = p.amount.calc(taxable_income)

        # Get number of eligible children dependents
        person = tax_unit.members
        meets_age_limit = person("age", period) < p.ineligible_age
        dependent = person("is_tax_unit_dependent", period)
        age_dependent_eligible = meets_age_limit & dependent
        count_eligible = tax_unit.sum(age_dependent_eligible)

        # Exclude married filing separately filers.
        filing_status = tax_unit("filing_status", period)
        filing_eligible = (
            filing_status != filing_status.possible_values.SEPARATE
        )

        # Calculate total child tax credit
        return count_eligible * amount_per_qualifying_child * filing_eligible

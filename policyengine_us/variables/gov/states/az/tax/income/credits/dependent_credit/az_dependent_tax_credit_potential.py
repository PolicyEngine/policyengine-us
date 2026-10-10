from policyengine_us.model_api import *


class az_dependent_tax_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona dependent tax credit"
    unit = USD
    reference = (
        "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01073-01.htm",
        "https://www.azleg.gov/ars/43/01001.htm",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.az.tax.income.credits.dependent_credit
        # A.R.S. 43-1001(3) gives "dependent" the IRC 152 meaning, and under
        # IRC 152(b)(1) a return on which the filer (or, if joint, either
        # spouse) can be claimed as a dependent has no dependents.
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        dependent = person("is_tax_unit_dependent", period) & ~filer_is_dependent
        age = person("age", period)
        dependent_amount = p.amount.calc(age) * dependent
        amount = tax_unit.sum(dependent_amount)
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        reduction_start = p.reduction.start[filing_status]
        excess = max_(income - reduction_start, 0)
        increments = np.ceil(excess / p.reduction.increment)
        reduction_percentage = min_(increments * p.reduction.percentage, 1)
        return amount * (1 - reduction_percentage)

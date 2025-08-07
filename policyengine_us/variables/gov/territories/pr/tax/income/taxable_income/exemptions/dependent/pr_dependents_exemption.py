from policyengine_us.model_api import *


class pr_dependents_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico dependents exemption"
    reference = "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=2"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR

    def formula(tax_unit, period, parameters):
        # line 8
        dependents = add(
            tax_unit, period, ["pr_eligible_dependent_for_exemption"]
        )
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.exemptions.dependent.amount
        amount = where(
            filing_status == filing_status.possible_values.SEPARATE,
            p.separate,
            p.non_separate,
        )
        return dependents * amount

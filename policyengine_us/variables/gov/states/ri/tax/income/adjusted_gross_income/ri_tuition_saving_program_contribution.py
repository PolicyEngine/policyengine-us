from policyengine_us.model_api import *


class ri_tuition_saving_program_contribution(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island Tuition Saving Program Contribution"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://webserver.rilin.state.ri.us/Statutes/title44/44-30/44-30-12.HTM"
        # (c),(4),(i)
    )
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        investment_amount = tax_unit("investment_in_529_plan", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.ri.tax.income.adjusted_gross_income.subtractions.tuition_saving_program_contributions
        cap = p.max_amount[filing_status]
        return min_(investment_amount, cap)

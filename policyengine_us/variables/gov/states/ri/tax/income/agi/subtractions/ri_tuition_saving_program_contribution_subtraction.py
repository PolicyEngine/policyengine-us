from policyengine_us.model_api import *


class ri_tuition_saving_program_contribution_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island tuition saving program contribution subtraction"
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
        ).gov.states.ri.tax.income.agi.subtractions.tuition_saving_program_contributions
        return min_(investment_amount, p.cap[filing_status])

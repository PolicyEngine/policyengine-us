from policyengine_us.model_api import *


class ri_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island Child Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.RI
    reference = "https://webserver.rilegislature.gov/BillText/BillText26/HouseText26/H7127Aaa.pdf#page=131"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.credits.ctc
        filing_status = tax_unit("filing_status", period)
        ri_agi = tax_unit("ri_agi", period)
        children = tax_unit("ri_ctc_eligible_children", period)
        maximum = children * p.amount

        threshold = p.phase_out.threshold[filing_status]
        increment = p.phase_out.increment[filing_status]
        excess = max_(ri_agi - threshold, 0)
        increments = np.ceil(excess / increment)
        phase_out_rate = min_(increments * p.phase_out.rate, 1)

        return maximum * (1 - phase_out_rate)

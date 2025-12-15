from policyengine_us.model_api import *


class mn_cdcc_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota child and dependent care expense credit phase out"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-02/m1cd_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1cd_22_0.pdf"
    )
    defined_for = "mn_cdcc_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.cdcc
        dep_count = tax_unit("mn_cdcc_dependent_count", period)
        # calculate pre-phaseout credit amount
        agi = tax_unit("adjusted_gross_income", period)
        # calculate post-phaseout credit amount
        excess_agi = max_(0, agi - p.phaseout_threshold)
        reduced_agi = excess_agi * p.phaseout_rate
        reduced_base_amount = p.reduced_base_amount.calc(dep_count)
        return max_(0, reduced_base_amount - reduced_agi)

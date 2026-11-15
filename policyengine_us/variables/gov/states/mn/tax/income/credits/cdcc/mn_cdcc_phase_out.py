from policyengine_us.model_api import *


def _calculate_mn_cdcc_phase_out(tax_unit, period, p, phaseout_threshold):
    dep_count = tax_unit("mn_cdcc_dependent_count", period)
    # calculate pre-phaseout credit amount
    agi = tax_unit("adjusted_gross_income", period)
    # calculate post-phaseout credit amount
    excess_agi = max_(0, agi - phaseout_threshold)
    reduced_agi = excess_agi * p.phaseout_rate
    reduced_base_amount = p.reduced_base_amount.calc(dep_count)
    return max_(0, reduced_base_amount - reduced_agi)


class mn_cdcc_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota child and dependent care expense credit phase out"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/2017/cite/290.067#stat.290.067.1",
        "https://www.revisor.mn.gov/laws/2017/1/1/",
        "https://www.revenue.state.mn.us/sites/default/files/2018-11/m1cd_18.pdf#page=3",
        "https://www.revenue.state.mn.us/sites/default/files/2019-12/m1cd_19.pdf#page=3",
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1cd_20.pdf#page=3",
        "https://www.revenue.state.mn.us/sites/default/files/2023-02/m1cd_21.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1cd_22_0.pdf",
    )
    defined_for = "mn_cdcc_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.cdcc
        return _calculate_mn_cdcc_phase_out(tax_unit, period, p, p.phaseout_threshold)

    def formula_2017(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.cdcc
        return _calculate_mn_cdcc_phase_out(
            tax_unit, period, p, p.historical_phaseout_threshold
        )

    def formula_2021(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.cdcc
        return _calculate_mn_cdcc_phase_out(tax_unit, period, p, p.phaseout_threshold)

from policyengine_us.model_api import *


class ca_amti(Variable):
    value_type = float
    entity = TaxUnit
    label = "California alternative minimum taxable income"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-540-p.pdf"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ca.tax.income.alternative_minimum_tax
        p2 = parameters(period).gov.irs.income.amt.capital_gains

        amti_before_ded = tax_unit("ca_pre_exemption_amti", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        amti_above_threshold = (
            amti_before_ded > p.exemption.amt_threshold.upper[filing_status]
        )
        reduced_amti = max_(amti_before_ded - p.exemption.amt_threshold.upper[filing_status], 0)
        separate_amti_calc = min_(
            (reduced_amti * p2.capital_gain_excess_tax_rate,
            p.exemption.amount[filing_status],)
        )

        # line 21
        return where(
            separate & amti_above_threshold,
            separate_amti_calc + amti_before_ded,
            amti_before_ded,
        )

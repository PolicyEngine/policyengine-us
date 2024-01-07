from policyengine_us.model_api import *


class ca_amti_calc(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA alternative minimum taxable income final calculation"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-540-p.pdf"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ca.tax.income.alternative_minimum_tax
        p2 = parameters(period).gov.irs.income.amt.capital_gains

        amti_before_ded = tax_unit("ca_amti", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        separate_threshold = (
            amti_before_ded > p.exemption.amt_threshold.upper[filing_status]
        )
        separate_amti_calc = min_(
            (amti_before_ded - p.exemption.amt_threshold.upper[filing_status])
            * p2.capital_gain_excess_tax_rate,
            p.exemption.amount[filing_status],
        )

        # line 21
        return where(
            separate & separate_threshold,
            separate_amti_calc + amti_before_ded,
            amti_before_ded,
        )

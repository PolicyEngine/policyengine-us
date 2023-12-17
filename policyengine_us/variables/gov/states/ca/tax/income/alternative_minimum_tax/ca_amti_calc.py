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

        amti_before_ded = tax_unit("ca_amti", period)
        separate = filing_status == filing_status.possible_values.SEPARATE

        return where(
            separate
            & (
                amti_before_ded
                > p.exemption_amt_upper_threshold[filing_status]
            ),
            min_(
                (
                    amti_before_ded
                    - p.exemption_amt_upper_threshold[filing_status]
                )
                * p.amti_rate,
                p.exemption_amt[filing_status],
            )
            + amti_before_ded,
            amti_before_ded,
        )

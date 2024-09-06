from policyengine_us.model_api import *


class tax_unit_ss_combined_income_excess(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Taxable Social Security combined income excess over base amount"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/86#b_1"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.social_security.taxability.threshold.base

        # The legislation directs the usage an income definition that is
        # a particularly modified AGI, plus half of gross Social Security
        # payments. We assume that the 'half' here is the same underlying
        # parameter as the lower taxability marginal rate (also 50% in the
        # baseline), and that they would be mechanically the same parameter.

        combined_income = tax_unit(
            "tax_unit_combined_income_for_social_security_taxability", period
        )
        filing_status = tax_unit("filing_status", period)

        status = filing_status.possible_values
        separate = filing_status == status.SEPARATE
        cohabitating = tax_unit("cohabitating_spouses", period)
        # Cohabitating married couples filing separately receive a base amount of 0
        base_amount = where(
            separate & cohabitating,
            p.separate_cohabitating,
            p.main[filing_status],
        )

        return max_(0, combined_income - base_amount)

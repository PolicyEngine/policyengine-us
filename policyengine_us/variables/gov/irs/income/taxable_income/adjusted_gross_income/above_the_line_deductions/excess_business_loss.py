from policyengine_us.model_api import *


class excess_business_loss(Variable):
    value_type = float
    entity = TaxUnit
    label = "Excess business loss"
    unit = USD
    documentation = (
        "Business losses above business income plus the Section 461(l) "
        "threshold, which loss_ald does not deduct (Form 461, line 16; "
        "Form 1040, Schedule 1, line 8p)."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/461#l",
        "https://www.irs.gov/pub/irs-prior/f461--2025.pdf",
    )

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        threshold = parameters(period).gov.irs.ald.loss.max[filing_status]
        # The same head and spouse business items as loss_ald. The excess of
        # aggregate business deductions over aggregate business income is
        # the negative of their net total.
        net_business_income = tax_unit_non_dep_add(
            tax_unit,
            period,
            [
                "total_self_employment_income",
                "farm_operations_income",
                "rental_income",
                "farm_rent_income",
                "estate_income",
                "partnership_s_corp_income",
                "other_net_gain",
            ],
        )
        return max_(0, -net_business_income - threshold)

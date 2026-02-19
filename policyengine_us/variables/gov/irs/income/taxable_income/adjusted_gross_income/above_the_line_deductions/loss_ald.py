from policyengine_us.model_api import *


class loss_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Business loss ALD"
    unit = USD
    documentation = "Above-the-line deduction from gross income for business and capital losses."
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/165",
        "https://www.law.cornell.edu/uscode/text/26/461#l",
    )

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        # Section 461(l) excess business loss limitation
        max_business_loss = parameters(period).gov.irs.ald.loss.max[
            filing_status
        ]
        person = tax_unit.members

        # Self-employment losses
        indiv_se_loss = max_(0, -person("self_employment_income", period))
        self_employment_loss = tax_unit.sum(indiv_se_loss)

        # Partnership/S-corp losses (Schedule E)
        indiv_scorp_loss = max_(
            0, -person("partnership_s_corp_income", period)
        )
        partnership_s_corp_loss = tax_unit.sum(indiv_scorp_loss)

        # Total business losses subject to Section 461(l) limitation
        total_business_loss = self_employment_loss + partnership_s_corp_loss
        limited_business_loss = min_(total_business_loss, max_business_loss)

        # Capital losses have separate limit under Section 1211 ($3,000)
        limited_capital_loss = tax_unit("limited_capital_loss", period)

        return limited_business_loss + limited_capital_loss

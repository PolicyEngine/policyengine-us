from policyengine_us.model_api import *


class loss_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Business loss ALD"
    unit = USD
    documentation = "Above-the-line deduction from gross income for business losses."
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/461#l",
        "https://www.law.cornell.edu/uscode/text/26/461#l_4",
    )

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        max_loss = parameters(period).gov.irs.ald.loss.max[filing_status]
        person = tax_unit.members
        indiv_se_loss = max_(0, -person("self_employment_income", period))
        self_employment_loss = tax_unit.sum(indiv_se_loss)
        indiv_se_gain = max_(0, person("self_employment_income", period))
        self_employment_gain = tax_unit.sum(indiv_se_gain)
        indiv_ps_loss = max_(0, -person("partnership_s_corp_income", period))
        partnership_s_corp_loss = tax_unit.sum(indiv_ps_loss)
        indiv_ps_gain = max_(0, person("partnership_s_corp_income", period))
        partnership_s_corp_gain = tax_unit.sum(indiv_ps_gain)
        business_loss = self_employment_loss + partnership_s_corp_loss
        business_gain = self_employment_gain + partnership_s_corp_gain
        allowed_business_loss = min_(business_loss, business_gain + max_loss)
        limited_capital_loss = tax_unit("limited_capital_loss", period)
        # Capital losses are deductible in AGI, but excluded from the
        # section 461(l) excess business loss limitation.
        return allowed_business_loss + limited_capital_loss

from policyengine_us.model_api import *


class loss_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Business loss ALD"
    unit = USD
    documentation = (
        "Above-the-line deduction from gross income for business and capital losses."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/165",
        "https://www.law.cornell.edu/uscode/text/26/461#l",
    )

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        # Section 461(l) excess business loss limitation
        threshold_amount = parameters(period).gov.irs.ald.loss.max[filing_status]
        person = tax_unit.members

        # Section 461(l) compares business deductions to business gross
        # income/gains plus the threshold amount. In this model, positive
        # business amounts flow into gross income and losses are deducted here,
        # so allowable business losses are capped at business income plus
        # the threshold.
        indiv_se_income = max_(0, person("total_self_employment_income", period))
        indiv_se_loss = max_(0, -person("total_self_employment_income", period))
        self_employment_income = tax_unit.sum(indiv_se_income)
        self_employment_loss = tax_unit.sum(indiv_se_loss)

        # Schedule F farm business income/losses.
        indiv_farm_income = max_(0, person("farm_operations_income", period))
        indiv_farm_loss = max_(0, -person("farm_operations_income", period))
        farm_income = tax_unit.sum(indiv_farm_income)
        farm_loss = tax_unit.sum(indiv_farm_loss)

        # Schedule E rental, farm-rent, and estate/trust items.
        indiv_rental_income = max_(0, person("rental_income", period))
        indiv_rental_loss = max_(0, -person("rental_income", period))
        rental_income = tax_unit.sum(indiv_rental_income)
        rental_loss = tax_unit.sum(indiv_rental_loss)

        indiv_farm_rent_income = max_(0, person("farm_rent_income", period))
        indiv_farm_rent_loss = max_(0, -person("farm_rent_income", period))
        farm_rent_income = tax_unit.sum(indiv_farm_rent_income)
        farm_rent_loss = tax_unit.sum(indiv_farm_rent_loss)

        indiv_estate_income = max_(0, person("estate_income", period))
        indiv_estate_loss = max_(0, -person("estate_income", period))
        estate_income = tax_unit.sum(indiv_estate_income)
        estate_loss = tax_unit.sum(indiv_estate_loss)

        # Partnership/S-corp losses (Schedule E)
        indiv_scorp_income = max_(0, person("partnership_s_corp_income", period))
        indiv_scorp_loss = max_(0, -person("partnership_s_corp_income", period))
        partnership_s_corp_income = tax_unit.sum(indiv_scorp_income)
        partnership_s_corp_loss = tax_unit.sum(indiv_scorp_loss)

        other_net_gain = tax_unit("other_net_gain", period)
        other_business_gain = max_(0, other_net_gain)
        other_business_loss = max_(0, -other_net_gain)

        # Total business losses subject to Section 461(l) limitation
        total_business_income = (
            self_employment_income
            + farm_income
            + rental_income
            + farm_rent_income
            + estate_income
            + partnership_s_corp_income
            + other_business_gain
        )
        total_business_loss = (
            self_employment_loss
            + farm_loss
            + rental_loss
            + farm_rent_loss
            + estate_loss
            + partnership_s_corp_loss
            + other_business_loss
        )
        max_deductible_business_loss = total_business_income + threshold_amount
        limited_business_loss = min_(total_business_loss, max_deductible_business_loss)

        # Capital losses have separate limit under Section 1211 ($3,000)
        limited_capital_loss = tax_unit("limited_capital_loss", period)

        return limited_business_loss + limited_capital_loss

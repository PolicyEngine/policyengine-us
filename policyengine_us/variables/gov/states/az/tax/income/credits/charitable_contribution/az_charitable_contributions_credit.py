from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)

class az_charitable_contributions_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona charitable contributions credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = "https://law.justia.com/codes/arizona/2022/title-43/section-43-1088/"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.credits.charitable_contribution.ceiling
        charitable_contributions = tax_unit(
            "az_charitable_contributions_to_qualifying_charitable_organizations",
            period,
        )
        foster_care_contributions = tax_unit(
            "az_charitable_contributions_to_qualifying_foster_care_organizations",
            period,
        )
        filing_status = tax_unit("filing_status", period)
        capped_charitable_contributions = min_(
            charitable_contributions, p.qualifying_organization[filing_status]
        )
        capped_foster_care_contributions = min_(
            foster_care_contributions, p.qualifying_foster[filing_status]
        )
        return capped_charitable_contributions + capped_foster_care_contributions


class az_charitable_contributions_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona charitable contributions credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = "https://law.justia.com/codes/arizona/2022/title-43/section-43-1088/"

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.az.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "az_income_tax_before_non_refundable_credits",
            "az_charitable_contributions_credit",
            "az_charitable_contributions_credit_potential",
        )

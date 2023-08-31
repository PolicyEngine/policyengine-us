from policyengine_us.model_api import *


class az_charitable_contributions_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona charitable contributions credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = (
        "https://law.justia.com/codes/arizona/2022/title-43/section-43-1088/"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.credits.charitable_contribution.ceiling
        filing_status = tax_unit("filing_status", period)
        foster_care = add(
            tax_unit,
            period,
            ["foster_care_charitable_organization"],
        )
        charitable_contributions = add(
            tax_unit,
            period,
            ["charitable_cash_donations", "charitable_non_cash_donations"],
        )
        cap = where(
            foster_care, p.qualifying_foster, p.qualifying_organization
        )

        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        capped_credit = min_(charitable_contributions, cap)

        return where(
            separate, capped_credit / p.separate_divisor, capped_credit
        )

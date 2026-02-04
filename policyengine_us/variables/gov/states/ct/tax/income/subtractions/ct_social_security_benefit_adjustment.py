from policyengine_us.model_api import *


class ct_social_security_benefit_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Connecticut social security benefit adjustment"
    reference = (
        "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-701",
        "https://portal.ct.gov/-/media/DRS/Forms/2024/Income/CT-1040-Instructions_1224.pdf#page=24",
    )
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.ct.tax.income.subtractions.social_security

        # Part A: Gross Social Security
        gross_social_security = tax_unit("tax_unit_social_security", period)

        # Part B: Combined income excess
        ss_combined_income_excess = tax_unit(
            "tax_unit_ss_combined_income_excess", period
        )

        # Part C: Lesser of gross SS and combined income excess
        capped_social_security = min_(
            gross_social_security, ss_combined_income_excess
        )

        # Part D: Apply CT rate to capped amount
        capped_social_security_portion = capped_social_security * p.rate

        # Part E: Federal taxable SS (Line 18 from federal SS worksheet)
        federal_taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security", period
        )

        # Part F: Reduced taxable SS
        reduced_taxable_social_security = max_(
            federal_taxable_social_security - capped_social_security_portion,
            0,
        )

        # Filers with AGI below the threshold can subtract the full amount
        # of their taxable social security benefits
        agi = tax_unit("adjusted_gross_income", period)
        full_adjustment_eligible = agi < p.reduction_threshold[filing_status]

        return where(
            full_adjustment_eligible,
            federal_taxable_social_security,
            reduced_taxable_social_security,
        )

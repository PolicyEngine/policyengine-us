from policyengine_us.model_api import *


class ct_social_security_benefit_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Connecticut social security benefit adjustment"
    reference = (
        # Connecticut General Statutes, Chapter 229, Sec. 12-701, (20), (b), (x), (iii) and (iv)
        "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-701"
        # 2022 Form CT-1040 Connecticut Resident Income Tax Return Instructions
        "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/2022-CT-1040-Instructions_1222.pdf#page=24"
    )
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        # Part A
        social_security = tax_unit("tax_unit_social_security", period)
        # Part B
        p_irs = parameters(period).gov.irs.social_security.taxability
        ss_combined_income_excess = tax_unit(
            "tax_unit_ss_combined_income_excess", period
        )
        # Part C
        capped_social_security = min_(
            social_security, ss_combined_income_excess
        )
        # Part D
        p = parameters(
            period
        ).gov.states.ct.tax.income.subtractions.social_security
        capped_social_security_portion = capped_social_security * p.rate
        # Part E (Line 18 from federal social security worksheet)
        gross_ss = tax_unit("tax_unit_social_security", period)
        adjusted_gross_social_security = gross_ss * p_irs.rate.additional
        # Part F
        reduced_taxable_social_security = max_(
            adjusted_gross_social_security - capped_social_security_portion,
            0,
        )
        # Filers with AGI below the threshold can subtract the full amount of their
        # taxable social security benefits
        agi = tax_unit("adjusted_gross_income", period)
        full_adjustment_eligible = agi < p.reduction_threshold[filing_status]
        taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        return where(
            full_adjustment_eligible,
            taxable_social_security,
            reduced_taxable_social_security,
        )

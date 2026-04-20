from policyengine_us.model_api import *


class wa_working_families_tax_credit_age_expansion_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Washington Working Families Tax Credit via age expansion"
    definition_period = YEAR
    reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=60"
    defined_for = StateCode.WA

    def formula(tax_unit, period, parameters):
        # ESSB 6346 Sec. 901(2)(a)(ii)(D): individuals who would otherwise
        # qualify for EITC except for age can qualify if at least age 18.
        p = parameters(
            period
        ).gov.states.wa.tax.income.credits.working_families_tax_credit.age_expansion

        expansion_in_effect = p.in_effect
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        filer_meets_min_age = (age_head >= p.min_age) | (age_spouse >= p.min_age)
        investment_income_eligible = tax_unit("eitc_investment_income_eligible", period)
        filers_have_ssn = tax_unit(
            "filer_meets_eitc_identification_requirements", period
        )
        eitc_amount_before_take_up = min_(
            tax_unit("eitc_phased_in", period),
            max_(
                0,
                tax_unit("eitc_maximum", period) - tax_unit("eitc_reduction", period),
            ),
        )

        eitc = parameters.gov.irs.credits.eitc(period)
        if eitc.eligibility.separate_filer:
            filing_status_eligible = True
        else:
            filing_status = tax_unit("filing_status", period)
            filing_status_eligible = (
                filing_status != filing_status.possible_values.SEPARATE
            )

        return (
            expansion_in_effect
            & filer_meets_min_age
            & investment_income_eligible
            & filers_have_ssn
            & (eitc_amount_before_take_up > 0)
            & filing_status_eligible
        )

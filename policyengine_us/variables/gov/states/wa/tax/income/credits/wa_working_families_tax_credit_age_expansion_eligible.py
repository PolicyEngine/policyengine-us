from policyengine_us.model_api import *


class wa_working_families_tax_credit_age_expansion_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Washington Working Families Tax Credit via age expansion"
    definition_period = YEAR
    reference = "https://lawfilesext.leg.wa.gov/biennium/2025-26/Pdf/Bills/Senate%20Passed%20Legislature/6346-S.PL.pdf#page=61"
    defined_for = StateCode.WA

    def formula(tax_unit, period, parameters):
        # ESSB 6346 Sec. 901(2)(a)(ii)(D): individuals who do not meet the
        # EITC age requirement but are at least age 18 (effective 2029).
        p = parameters(
            period
        ).gov.states.wa.tax.income.credits.working_families_tax_credit.age_expansion

        expansion_in_effect = p.in_effect
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        filer_meets_min_age = (age_head >= p.min_age) | (age_spouse >= p.min_age)
        earned_income = tax_unit("filer_adjusted_earnings", period)
        has_earned_income = earned_income > 0

        return expansion_in_effect & filer_meets_min_age & has_earned_income

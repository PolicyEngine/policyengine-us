from policyengine_us.model_api import *


class social_security(Variable):
    value_type = float
    entity = TaxUnit
    label = "RI Social Security Modification"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/Social%20Security%20Worksheet_w.pdf"
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        age = tax_unit.members("age", period)
        birth_year = -(age - period.start.year)
        spouse = tax_unit.members("is_tax_unit_spouse", period)
        spouse_age = tax_unit.max(age * spouse)
        spouse_birth_year = -(spouse_age - period.start.year)
        p = parameters(
            period
        ).gov.states.ri.tax.income.adjusted_gross_income.subtractions.social_security

        # Age-based eligibility.
        
        age_conditions = birth_year <= p.birth_date_limit
        spouse_pass_age_threshold = spouse_birth_year <= p.birth_date_limit
        spouse_eligible = spouse & spouse_pass_age_threshold
        age_is_eligible = age_conditions | spouse_eligible
        both_age_is_eligible = age_conditions & spouse_eligible

        # Status eligibility.
        status_is_eligible = income < p.income_amount[filing_status]

        total_social_security = tax_unit("tax_unit_social_security", period)
        taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        spouse_total_ss = tax_unit.max(total_social_security * spouse)
        final_ss = where(age_is_eligible & age_conditions, total_social_security,
        where(age_is_eligible & spouse_eligible, spouse_total_ss,0))

        mod_social_security = where(age_is_eligible & status_is_eligible, taxable_social_security*(final_ss/total_social_security),
        where(both_age_is_eligible & status_is_eligible, taxable_social_security,0))



        return mod_social_security
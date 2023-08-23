from policyengine_us.model_api import *
import numpy as np


class ri_social_security_modification(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island Social Security Modification"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/Social%20Security%20Worksheet_w.pdf"
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        age = person("age", period)
        birth_year = period.start.year - age

        p = parameters(
            period
        ).gov.states.ri.tax.income.adjusted_gross_income.subtractions.social_security

        # Age-based eligibility.
        age_conditions = birth_year <= p.birth_date_limit
        head_eligible = age_conditions & is_head
        spouse_eligible = age_conditions & is_spouse
        age_is_eligible = head_eligible | spouse_eligible
        both_age_is_eligible = head_eligible & spouse_eligible

        # Status eligibility.
        status_is_eligible = income < p.income_amount[filing_status]

        total_social_security = person("social_security", period)

        taxable_social_security = person("taxable_social_security", period)

        head_total_ss = tax_unit.sum(total_social_security * is_head)

        spouse_total_ss = tax_unit.sum(total_social_security * is_spouse)

        head_social_security = where(head_eligible, head_total_ss, 0)

        final_ss = where(
            spouse_eligible,
            spouse_total_ss,
            head_social_security,
        )

        final_ss = tax_unit.max(final_ss)

        percentage_social_security = np.zeros_like(head_total_ss)
        mask = head_total_ss != 0
        percentage_social_security[mask] = final_ss[mask] / head_total_ss[mask]

        head_taxable_ss = tax_unit.sum(taxable_social_security * is_head)
        eligible_mod_ss = age_is_eligible & status_is_eligible
        head_mod_social_security = where(
            eligible_mod_ss,
            head_taxable_ss * percentage_social_security,
            0,
        )
        eligible_spouse_mod_ss = both_age_is_eligible & status_is_eligible
        final_mod_ss = where(
            eligible_spouse_mod_ss,
            head_taxable_ss,
            head_mod_social_security,
        )

        return tax_unit.max(final_mod_ss)

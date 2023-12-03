from policyengine_us.model_api import *


class ri_social_security_modification(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island Social Security Modification"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/Social%20Security%20Worksheet_w.pdf"
    defined_for = "ri_social_security_modification_eligible"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period)
        birth_year = period.start.year - age

        p = parameters(
            period
        ).gov.states.ri.tax.income.adjusted_gross_income.subtractions.social_security.threshold

        # Age eligibility.
        age_conditions = birth_year <= p.birth_year
        head_or_spouse_eligible = head_or_spouse & age_conditions

        total_social_security = person("social_security", period)
        final_ss = tax_unit.sum(total_social_security * head_or_spouse_eligible)
        total_ss = tax_unit.sum(total_social_security * head_or_spouse)

        percentage_social_security = np.zeros_like(total_ss)
        mask = total_ss != 0
        percentage_social_security[mask] = final_ss[mask] / total_ss[mask]
        
        taxable_social_security = person("taxable_social_security", period)
        total_taxable_ss = tax_unit.sum(taxable_social_security * head_or_spouse)

        return total_taxable_ss * percentage_social_security

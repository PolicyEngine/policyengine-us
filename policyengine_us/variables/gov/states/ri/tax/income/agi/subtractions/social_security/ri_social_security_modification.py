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
        birth_year = person("birth_year", period)

        p = parameters(
            period
        ).gov.states.ri.tax.income.agi.subtractions.social_security.limit

        aged = birth_year <= p.birth_year
        head_or_spouse_aged = head_or_spouse & aged

        total_social_security = person("social_security", period)
        aged_head_or_spouse_ss = tax_unit.sum(
            total_social_security * head_or_spouse_aged
        )
        head_or_spouse_ss = tax_unit.sum(
            total_social_security * head_or_spouse
        )
        # The social security modification is calculated as the percentage of social security
        # received by the aged head or spouse relative to the total social security received
        aged_ss_as_a_percentage_of_total_ss = np.zeros_like(head_or_spouse_ss)
        mask = head_or_spouse_ss != 0
        aged_ss_as_a_percentage_of_total_ss[mask] = (
            aged_head_or_spouse_ss[mask] / head_or_spouse_ss[mask]
        )

        taxable_social_security = person("taxable_social_security", period)
        head_or_spouse_taxable_ss = tax_unit.sum(
            taxable_social_security * head_or_spouse
        )
        return head_or_spouse_taxable_ss * aged_ss_as_a_percentage_of_total_ss

from openfisca_us.model_api import *


class massachusetts_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA gross income"
    unit = USD
    definition_period = YEAR
    is_eligible = in_state("MA")
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-2"

    def formula(tax_unit, period, parameters):
        # Mass. General Laws c.62 § 2(a)
        federal_gross_income = tax_unit("irs_gross_income", period)
        foreign_earned_income = tax_unit("foreign_earned_income_exclusion", period)
        social_security_in_agi = add(tax_unit, period, ["taxable_social_security"])
        deductions = foreign_earned_income + social_security_in_agi
        return max_(0, federal_gross_income - deductions)
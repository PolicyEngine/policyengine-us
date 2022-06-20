from openfisca_us.model_api import *


class ma_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-2"

    def formula(tax_unit, period, parameters):
        # Mass. General Laws c.62 § 2(a)
        federal_gross_income = add(tax_unit, period, ["irs_gross_income"])
        foreign_earned_income = tax_unit(
            "foreign_earned_income_exclusion", period
        )
        social_security_in_agi = add(
            tax_unit, period, ["taxable_social_security"]
        )
        deductions = foreign_earned_income + social_security_in_agi
        return max_(0, federal_gross_income - deductions)

from policyengine_us.model_api import *


class in_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN deductions"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3"

    formula = sum_of_variables(
        [
            "in_renters_deduction",
            "in_homeowners_property_tax_deduction",
            "salt_refund_last_year",
            "us_govt_interest",
            "tax_unit_taxable_social_security",  # includes railroad retirement benefits
            "in_military_service_deduction",
            "in_nonpublic_school_deduction",
            "in_nol",
            "in_unemployment_compensation_deduction",
            "in_other_deductions",
        ]
    )

from openfisca_us.model_api import *


class in_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN deductions"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3"


    def formula(in_deductions, period, parameters):
        in_renters_deduction = tax_unit("in_renters_deduction", period)
        in_homeowners_property_tax_deduction = tax_unit("in_homeowners__property_taxdeduction", period)
        salt_refund = tax_unit("salt_refund", period)
        us_gov_interest = tax_unit("us_gov_interest", period)
        taxable_social_security = tax_unit("taxable_social_security", period)
        taxable_railroad_retirement = tax_unit("taxable_railroad_retirement", period)
        in_military_service_deduction = tax_unit("in_military_service_deduction", period)
        in_private_homeschool_deduction = tax_unit("in_private_homeschool_deduction", period)
        in_nol_deduction = tax_unit("in_nol_deduction", period)
        in_nontaxable_unemployment_deduction = tax_unit("in_nontaxable_unemployment_deduction", period)
        in_other_deductions = tax_unit("in_other_deduction", period)
        return (in_renters_deduction
                + in_homeowners_property_tax_deduction 
                + salt_refund
                + us_gov_interest
                + taxable_social_security
                + taxable_railroad_retirement
                + in_military_service_deduction
                + in_private_homeschool_deduction
                + in_nol_deduction
                + in_nontaxable_unemployment_deduction
                + in_other_deductions)
                
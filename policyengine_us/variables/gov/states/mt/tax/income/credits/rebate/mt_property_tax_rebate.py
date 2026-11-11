from policyengine_us.model_api import *


class mt_property_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana property tax rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=5"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        # Modeling limitation: this does not encode the statutory eligibility
        # conditions for the rebate (principal residence; at least 7 months of
        # ownership and occupancy during the year; property taxes billed and
        # paid; a timely rebate claim). household_state_benefits and
        # spm_unit_benefits count the rebate through state_property_tax_refunds,
        # so for tax years 2022 through 2024 they credit it to every Montana
        # tax unit with real estate taxes, claimants or not.
        p = parameters(period).gov.states.mt.tax.income.credits.rebate.property
        person = tax_unit.members
        mt_property_tax = person("real_estate_taxes", period)
        tax_unit_mt_property_tax = tax_unit.sum(mt_property_tax)
        return min_(p.amount, tax_unit_mt_property_tax)

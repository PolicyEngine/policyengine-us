from policyengine_us.model_api import *
from policyengine_us.tools.mt_separate_return import (
    mt_allocate_dependent_exemptions,
)


class mt_taxable_income_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana taxable income when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    defined_for = "mt_married_filing_separately_on_same_return_eligible"
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=1",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=16",
    )

    def formula(person, period, parameters):
        pre_dependent_exemption_income = person(
            "mt_pre_dependent_exemption_taxable_income_indiv", period
        )
        # The dependent exemptions are allocated optimally between the head
        # and spouse (mt_allocate_dependent_exemptions).
        return mt_allocate_dependent_exemptions(
            person, period, pre_dependent_exemption_income
        )

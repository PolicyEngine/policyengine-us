from policyengine_us.model_api import *
from policyengine_us.tools.mt_filing_choice import mt_separate_filing_is_cheaper


class mt_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "married couple files separately on Montana tax return"
    documentation = (
        "Married taxpayers may choose joint or separate filing on Montana Form 2. "
        "PolicyEngine chooses separate filing when its combined tax falls "
        "below the joint tax by more than one cent. PolicyEngine treats "
        "savings of at most one cent as ties and keeps joint filing."
    )
    reference = "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=11"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income
        if p.married_filing_separately_on_same_return_allowed:
            itax_indiv = add(tax_unit, period, ["mt_income_tax_indiv"])
            itax_joint = tax_unit("mt_income_tax_joint", period)
            return mt_separate_filing_is_cheaper(itax_indiv, itax_joint)
        return False

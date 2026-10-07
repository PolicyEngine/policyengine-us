from policyengine_us.model_api import *


class mt_agi_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana Adjusted Gross Income for each individual"
    unit = USD
    definition_period = YEAR
    reference = (
        # Filing separately: each column is its own return
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=12",
        # Borrowed for dependents' income: parents filing separately report a
        # child's income on the return of the parent with the greater
        # taxable income
        "https://www.law.cornell.edu/uscode/text/26/1#g_5_B",
        "https://www.irs.gov/instructions/i8814",
    )
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    def formula(person, period, parameters):
        agi = person("adjusted_gross_income_person", period)
        additions = person("mt_additions", period)
        subtractions = person("mt_subtractions", period)
        reduced_agi = max_(agi + additions - subtractions, 0)
        # Montana taxable social security benefits can be either addition or subtraction
        # if mt_taxable_social security - taxable_social_security > 0, then addition, else subtraction

        p = parameters(period).gov.states.mt.tax.income.social_security
        if p.applies:
            # 2023 and before: apply lines 21-24 adjustment for social security
            taxable_ss = person("taxable_social_security", period)
            mt_taxable_ss = person("mt_taxable_social_security", period)
            adjusted_mt_ss_difference = mt_taxable_ss - taxable_ss
            tax_unit_mt_agi = max_(reduced_agi + adjusted_mt_ss_difference, 0)
        else:
            # 2024 and after: no longer apply the social security adjustment
            tax_unit_mt_agi = reduced_agi

        # The dependents' income the model counts here goes on the return of
        # the spouse with the greater income (a modelling convention; see the
        # helper). The instructions' Line 5 exclusion of a child's income
        # reported on federal Form 8814 is not modelled.
        return move_dependent_amounts_to_filer(person, period, tax_unit_mt_agi)

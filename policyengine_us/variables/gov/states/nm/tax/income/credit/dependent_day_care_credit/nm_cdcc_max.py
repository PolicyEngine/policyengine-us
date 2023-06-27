from policyengine_us.model_api import *


class nm_cdcc_max(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum NM child day care credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM
    reference = 'https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf' #p63

    def formula(tax_unit, period, parameters):

        ################################################################################################################
        # Limitations:
        # Taxpayer may claim ccdc if
        #   (1): singly or together with a spouse frnishes over half the cost of maintainingu
        #        the household for one or more qualifying dependents for any period in the taxable
        #        year for which the credit is claimed;
        #   (2): is gainfully employed for any period for which the credit is claimed or, if a joint
        #        return is filed, both spouses are gainfully employed or one is disabled for any period
        #        for which the credit is claimed;
        #   (3): compensates a caregiver for child day care for a qualifying dependent to enable such
        #        resident together with the resident's spouse, if any and if not disabled, to be gainfully employed
        #   (4): is not a recipient of public assistance under a program of aid to families with dependent children,
        #        a program under the New Mexico Works Act or any successor program during any period for which the
        #        credit provided by this section is claimed
        #   (5): has a modified gross income, including child support payments, if any, of not more than the annual
        #        income that would be derived from earnings at double the federal minimum wage.
        #
        # reference: https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf 
        #           (p65 section B)
        ################################################################################################################

        # Limitation(1)
        cdcc_expenses = tax_unit("cdcc_relevant_expenses", period)
        maintaining_the_household = tax_unit("nm_maintaining_household",period)
        eligible_1 = cdcc_expenses > (maintaining_the_household*0.5)

        # Limitation(2)&(3)
        person = tax_unit.members
        income = person("employment_income", period)
        income_eligible = income > 0 
        spouse = person("is_tax_unit_spouse", period) # 0: without spouse; 1: with spouse
        head = person("is_tax_unit_head", period)
        spouse_eligible = tax_unit.any(spouse * income_eligible)
        head_eligible = tax_unit.any(head * income_eligible)
        married_eligible = spouse_eligible and head_eligible
        
        head_disabled = tax_unit("head_is_disabled", period)
        spouse_disabled = tax_unit("spouse_is_disabled", period)
        is_disabled = head_disabled | spouse_disabled

        filing_status = tax_unit("filing_status", period)
        is_married = filing_status == filing_status.possible_values.JOINT
        married_status_eligible = where(is_married, married_eligible , head_eligible)
        eligible_2_3 = married_status_eligible | is_disabled

        #Limitation(4)
        public_assistance_income = tax_unit("nm_public_assistance_income",period)
        eligible_4 = public_assistance_income == 0

        #Limitation(5)
        modified_gross_income = tax_unit('nm_modified_gross_income',period)
        federal_min_wage = parameters(period).gov.states.nm.tax.income.credits.cdcc.federal_minimum_wage
        eligible_5 = modified_gross_income < (federal_min_wage * 2)

        ###################################################################

        nm_cdcc = parameters(period).gov.states.nm.tax.income.credits.cdcc
        count_eligible = tax_unit("count_cdcc_eligible", period)
        nm_max = nm_cdcc.max.calc(count_eligible)
        limitations_status_eligible = eligible_1 & eligible_2_3 & eligible_4 & eligible_5
        nm_cap = where(limitations_status_eligible, nm_max, 0)
        

        return min_(cdcc_expenses, nm_cap)
    

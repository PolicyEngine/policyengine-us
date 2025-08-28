from policyengine_us.model_api import *


class tx_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Texas LIHEAP countable monthly income"
    documentation = (
        "Total monthly countable household income for Texas LIHEAP eligibility determination"
    )
    reference = "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf"
    defined_for = StateCode.TX
    unit = USD

    def formula(spm_unit, period, parameters):
        # Get all people in the SPM unit
        person = spm_unit.members
        
        # Employment income (convert annual to monthly)
        employment_income = person("employment_income", period.this_year)
        monthly_employment = spm_unit.sum(employment_income) / 12
        
        # Self-employment income (convert annual to monthly)
        self_employment_income = person("self_employment_income", period.this_year)
        monthly_self_employment = spm_unit.sum(self_employment_income) / 12
        
        # Social Security income (convert annual to monthly)
        social_security = person("social_security", period.this_year)
        monthly_social_security = spm_unit.sum(social_security) / 12
        
        # SSI income (convert annual to monthly)
        ssi = person("ssi", period.this_year)
        monthly_ssi = spm_unit.sum(ssi) / 12
        
        # TANF benefits (already monthly)
        tanf = spm_unit("tanf", period)
        
        # Unemployment compensation (convert annual to monthly)
        unemployment_compensation = person("unemployment_compensation", period.this_year)
        monthly_unemployment = spm_unit.sum(unemployment_compensation) / 12
        
        # Veterans benefits (convert annual to monthly)
        veterans_benefits = person("veterans_benefits", period.this_year)
        monthly_veterans = spm_unit.sum(veterans_benefits) / 12
        
        # Workers compensation (convert annual to monthly)
        workers_compensation = person("workers_compensation", period.this_year)
        monthly_workers_comp = spm_unit.sum(workers_compensation) / 12
        
        # Pension income (convert annual to monthly)
        taxable_pension_income = person("taxable_pension_income", period.this_year)
        monthly_pension = spm_unit.sum(taxable_pension_income) / 12
        
        # Calculate total monthly income
        return (
            monthly_employment +
            monthly_self_employment +
            monthly_social_security +
            monthly_ssi +
            tanf +
            monthly_unemployment +
            monthly_veterans +
            monthly_workers_comp +
            monthly_pension
        )
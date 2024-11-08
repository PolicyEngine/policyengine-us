
class ScUseTaxCountyGroup(Enum):
    GROUP1 = "one"
    GROUP2 = "two"
    GROUP3 = "three"
    GROUP4 = "default"  
  

class sc_use_tax_county_group(Variable):
    value_type = Enum
    entity = Household
    possible_values = ScUseTaxCountyGroup  
    default_value = ScUseTaxCountyGroup.GROUP4  
    definition_period = YEAR
    label = "SC use tax county group"

    def formula(household, period, parameters):
    
        county = household("county_str", period)
        
        group1_counties = parameters(
            period
        ).gov.states.sc.tax.income.use_tax.county_group.one  
        
        group2_counties = parameters(
            period
        ).gov.states.sc.tax.income.use_tax.county_group.two  
        
        group3_counties = parameters(
            period
        ).gov.states.sc.tax.income.use_tax.county_group.three  
        
        return select(
            [
                county in group1_counties,  
                county in group2_counties,  
                county in group3_counties,  
            ],
            [
                ScUseTaxCountyGroup.GROUP1,  
                ScUseTaxCountyGroup.GROUP2,  
                ScUseTaxCountyGroup.GROUP3,  
            ],
            default=ScUseTaxCountyGroup.GROUP4  
        )

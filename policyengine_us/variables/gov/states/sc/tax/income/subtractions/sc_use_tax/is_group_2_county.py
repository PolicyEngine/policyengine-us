class is_group2_county(Variable):
    value_type = bool
    entity = TaxUnit
    label = "In a South Carolina use tax region 2 county"
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://dor.sc.gov/resources-site/lawandpolicy/Documents/SC%20Sales%20Tax%20Manual.pdf"
    )
    
    def formula(household, period, parameters):
        county = household("county_str", period)
        group_2_counties = parameters(period).gov.states.sc.tax.income.use_tax.rate.county_group_2
        return np.isin(county, group_2_counties)

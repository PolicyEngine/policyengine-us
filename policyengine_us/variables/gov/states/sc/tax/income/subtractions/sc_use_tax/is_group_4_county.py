class is_group4_county(Variable):
    value_type = bool
    entity = TaxUnit
    label = "In a South Carolina use tax region 4 county"
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = 

    def formula(household, period, parameters):
        county = household("county_str", period)
        group_4_counties = parameters(period).gov.states.sc.tax.income.use_tax.rate.county_group_4
        return np.isin(county, group_4_counties)

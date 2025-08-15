from policyengine_us.model_api import *


class ScUseTaxCountyGroup(Enum):
    GROUP1 = "Group one"
    GROUP2 = "Group two"
    GROUP3 = "Group three"
    GROUP4 = "Group four"


class sc_use_tax_county_group(Variable):
    value_type = Enum
    entity = Household
    possible_values = ScUseTaxCountyGroup
    default_value = ScUseTaxCountyGroup.GROUP4
    definition_period = YEAR
    label = "South Carolina use tax county group"
    defined_for = StateCode.SC

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
                np.isin(county, group1_counties),
                np.isin(county, group2_counties),
                np.isin(county, group3_counties),
            ],
            [
                ScUseTaxCountyGroup.GROUP1,
                ScUseTaxCountyGroup.GROUP2,
                ScUseTaxCountyGroup.GROUP3,
            ],
            default=ScUseTaxCountyGroup.GROUP4,
        )

from policyengine_us.model_api import *


class ami(Variable):
    value_type = float
    entity = Household
    label = "Area median income"
    documentation = "Area median income for a four-person household"
    definition_period = YEAR

    def formula(household, period, parameters):
        # Only calculate for LA County and Denver County for now. Otherwise zero.
        in_la = household("in_la", period)
        in_denver = household("in_denver", period)
        # https://www.hcd.ca.gov/sites/default/files/docs/grants-and-funding/income-limits-2023.pdf
        LA_COUNTY_AMI = 98_200
        DENVER_COUNTY_AMI = 124_100
        return in_la * LA_COUNTY_AMI | in_denver * DENVER_COUNTY_AMI

from policyengine_us.model_api import *


class wi_cts_countable_resources(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin CTS individual countable resources"
    definition_period = MONTH
    unit = USD
    quantity_type = STOCK
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
    documentation = "Default covers modeled SSI liquid resources. Override with the CTS asset budget when it differs: include retirement assets, life insurance, nonhome real estate and vehicle equity after the $1,500 exemption for one vehicle; exclude the home, approved burial assets, student loans and protected tax refunds. SSI recipients are excluded at the group calculation."

    def formula(person, period, parameters):
        return person("ssi_countable_resources", period.this_year)

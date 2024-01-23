from policyengine_us.model_api import *


class mi_alternate_home_heating_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Michigan alternate home heating credit"
    definition_period = YEAR
    defined_for = StateCode.MI
    reference = (
        "https://www.michigan.gov/-/media/Pxroject/Websites/taxes/2022RM/IIT/MI-1040CR7.pdf?rev=84f72df3f8664b96903aa6b655dc34d2"
        "http://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a"
    )

    def formula(tax_unit, period, parameters):
        utilities_not_included_in_rent = ~tax_unit(
            "utilities_included_in_rent", period
        )
        household_resources = tax_unit("mi_household_resources", period)
        exemptions = tax_unit("mi_exemptions_count", period)

        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.home_heating.alternate
        resource_cap = p.household_resources.cap.calc(exemptions)
        resource_eligible = household_resources < resource_cap
        return utilities_not_included_in_rent & resource_eligible

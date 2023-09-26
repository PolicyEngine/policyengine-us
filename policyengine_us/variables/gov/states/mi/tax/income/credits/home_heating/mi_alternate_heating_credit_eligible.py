from policyengine_us.model_api import *


class mi_alternate_heating_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Michigan alternate heating credit"
    definition_period = YEAR
    defined_for = StateCode.MI
    reference = (
        "https://www.michigan.gov/-/media/Pxroject/Websites/taxes/2022RM/IIT/MI-1040CR7.pdf?rev=84f72df3f8664b96903aa6b655dc34d2"
        "http://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a"
    )
    def formula(tax_unit, period, parameters):
        return ~tax_unit("heating_costs_included_in_rent", period)

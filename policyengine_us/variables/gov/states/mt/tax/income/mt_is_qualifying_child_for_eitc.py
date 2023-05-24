from policyengine_us.model_api import *


class mt_is_qualifying_child_for_eitc(Variable):
    value_type = bool
    entity = Person
    label = "Child qualifies for EITC"
    definition_period = YEAR
    reference = https://www.montanalawhelp.org/resource/earned-income-tax-credit#iCB8804FF-2AEF-41B4-83EE-BBC12F45DCC0

    def formula(person, period):
        # CalEITC uses federal EITC rules regarding qualifying children
        #May have additional requirement
        #In addition, the child cannot file a joint return for the year (other than for a claim of refund). A child who is married generally will not be a qualifying child.
        return person("is_eitc_qualifying_child", period) & person(...)
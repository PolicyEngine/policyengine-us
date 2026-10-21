from policyengine_us.model_api import *


class ca_tanf_recipient_financial_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Recipient Financial Test"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://my.dpss.lacounty.gov/public/en/home/epolicy/program/calworks/income/earned-income-disregards.html"

    def formula(spm_unit, period, parameters):
        maximum_payment = spm_unit("ca_tanf_maximum_payment", period)
        countable_income = spm_unit("ca_tanf_countable_income_recipient", period)

        return countable_income < maximum_payment

from policyengine_us.model_api import *


class mt_aged_exemption_joint(Variable):
    value_type = int
    entity = TaxUnit
    label = "Montana aged exemptions when married filing jointly"
    definition_period = YEAR
    reference = "https://regulations.justia.com/states/montana/department-42/chapter-42-15/subchapter-42-15-4/rule-42-15-402/"
    defined_for = StateCode.MT

    adds = ["mt_aged_exemption_indiv"]
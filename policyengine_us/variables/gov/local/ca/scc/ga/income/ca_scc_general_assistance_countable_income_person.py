from policyengine_us.model_api import *


class ca_scc_general_assistance_countable_income_person(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "Santa Clara County General Assistance countable income for each person"
    defined_for = "is_tax_unit_head_or_spouse"
    reference = "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/09Income/Types_Income.htm"

    adds = "gov.local.ca.scc.general_assistance.countable_income.sources"

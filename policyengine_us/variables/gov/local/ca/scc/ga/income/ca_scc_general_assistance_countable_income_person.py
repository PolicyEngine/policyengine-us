from policyengine_us.model_api import *


class ca_scc_general_assistance_countable_income_person(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "Santa Clara County General Assistance countable income for each person"
    defined_for = "is_tax_unit_head_or_spouse"
    reference = (
        "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/09Income/Types_Income.htm",
        "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/02Application/Responsible_Relatives.htm",
    )

    def formula(person, period, parameters):
        sources = parameters(
            period
        ).gov.local.ca.scc.general_assistance.countable_income.sources
        receives_ssi = person("ssi", period) > 0
        return add(person, period, sources) * ~receives_ssi

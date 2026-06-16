from policyengine_us.model_api import *


class mo_ccs_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Missouri Child Care Subsidy countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.MO
    reference = (
        "https://web.archive.org/web/20211208073807id_/https://dese.mo.gov/childhood/quality-programs/child-care-subsidy/child-care-manual/2010/045/10",
    )

    adds = "gov.states.mo.dese.ccs.income.countable_income.sources"

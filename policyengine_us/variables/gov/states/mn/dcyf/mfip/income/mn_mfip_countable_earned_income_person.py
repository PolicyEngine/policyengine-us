from policyengine_us.model_api import *


class mn_mfip_countable_earned_income_person(Variable):
    value_type = float
    entity = Person
    label = "Minnesota MFIP countable earned income for each person"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256P.03#stat.256P.03.2",
        "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=cm_001818",
    )
    defined_for = StateCode.MN

    def formula(person, period, parameters):
        # Per MN DHS Combined Manual 0018.18:
        # "Disregard the 1st $65 of earned income per wage earner
        # plus half of the remaining earned income"
        p = parameters(
            period
        ).gov.states.mn.dcyf.mfip.income.earned_income_disregard
        gross_earned = person("tanf_gross_earned_income", period)
        after_flat = max_(gross_earned - p.flat_amount, 0)
        return after_flat * (1 - p.rate)

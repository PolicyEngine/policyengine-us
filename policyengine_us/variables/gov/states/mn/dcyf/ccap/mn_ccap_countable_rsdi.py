from policyengine_us.model_api import *


class mn_ccap_countable_rsdi(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Minnesota CCAP countable Retirement, Survivors, and Disability Insurance"
    definition_period = YEAR
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256P.06",
        "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=CCAP_0606",
    )

    def formula(person, period, parameters):
        # Minn. Stat. 256P.06, subd. 3(2)(xvi) counts, for chapter 142E
        # programs, only the RSDI amount that exceeds the monthly federal
        # maximum SSI payment. CCAP Policy Manual section 6.6 annualizes the
        # gross RSDI and deducts the SSI federal benefit rate from it. We apply
        # the individual rate to each recipient's own RSDI.
        p = parameters(period).gov.states.mn.dcyf.ccap.income.countable_income
        rsdi = add(person, period, p.rsdi_sources)
        monthly_fbr = parameters(period).gov.ssa.ssi.amount.individual
        return max_(rsdi - monthly_fbr * MONTHS_IN_YEAR, 0)

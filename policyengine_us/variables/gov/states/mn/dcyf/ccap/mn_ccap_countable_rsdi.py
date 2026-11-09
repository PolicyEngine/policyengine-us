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
        "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=CCAP_061524",
        "https://www.dhs.state.mn.us/main/idcplg?IdcService=GET_DYNAMIC_CONVERSION&RevisionSelectionMethod=LatestReleased&dDocName=cm_00171545",
    )

    def formula(person, period, parameters):
        # Minn. Stat. 256P.06, subd. 3(2)(xvi) counts, for chapter 142E
        # programs, only the RSDI amount that exceeds the monthly federal
        # maximum SSI payment. CCAP Policy Manual section 6.6 annualizes the
        # gross RSDI and deducts the SSI federal benefit rate from it; section
        # 6.15.24 gives that rate as $967 per month in 2025, the individual
        # rate. Combined Manual 0017.15.45 counts, for each client who receives
        # RSDI, only the amount above the SSI standard for a household of 1,
        # and its 09/2024 revision note applies the change to CCAP. We apply
        # the individual rate to each recipient's own RSDI.
        p = parameters(period).gov.states.mn.dcyf.ccap.income.countable_income
        rsdi = add(person, period, p.rsdi_sources)
        monthly_fbr = parameters(period).gov.ssa.ssi.amount.individual
        return max_(rsdi - monthly_fbr * MONTHS_IN_YEAR, 0)

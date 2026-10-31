from policyengine_us.model_api import *
from policyengine_us.variables.gov.states._spouses import state_couple_total


class or_ssp(Variable):
    value_type = float
    entity = Person
    label = "Oregon State Supplemental Payment"
    definition_period = MONTH
    unit = USD
    reference = (
        # ORS 411.704(1)(b), 411.706(1)
        "https://www.oregonlegislature.gov/bills_laws/ors/ors411.html",
        # PDF pages 1-2
        "https://ch461rules.odhs.oregon.gov/rules/461-155-0250.pdf#page=1",
        "https://ch461rules.odhs.oregon.gov/rules/461-155-0575.pdf",
        # PDF pages 1-3
        "https://ch461rules.odhs.oregon.gov/rules/461-155-0630.pdf#page=1",
        # PDF pages 1-3
        "https://ch461rules.odhs.oregon.gov/rules/461-155-0700.pdf#page=1",
        "https://ch461rules.odhs.oregon.gov/rules/461-160-0070.pdf",
        # 461-101-0010(17) defines OSIP as these special need payments.
        "https://ch461rules.odhs.oregon.gov/rules/461-101-0010.pdf#page=3",
        # DHS 2818 (10/2026)
        "https://sharedsystems.dhsoha.state.or.us/DHSForms/Served/de2818.pdf#page=583",
    )
    defined_for = StateCode.OR

    def formula(person, period, parameters):
        p = parameters(period).gov.states["or"].odhs.ssp
        federal = parameters(period).gov.ssa.ssi.amount
        # The OSIPM one-person adjusted income standard in OAR 461-155-0250(3)
        # currently equals the SSI federal benefit rate ($994 in 2026).
        standard = federal.individual
        category = person("or_ssp_category", period)
        c = category.possible_values
        income = person("or_ssp_countable_income", period)
        ssi = person("ssi", period)
        receives_ssi = (ssi > 0) | person("receives_ssi", period)
        in_home = (category == c.IN_HOME) & receives_ssi & (income == ssi)
        # Community care and SSI restoration amounts depend on the SSI payment,
        # so those paths require modeled SSI rather than reported receipt.
        care = (category == c.COMMUNITY_CARE) & (ssi > 0)
        # OAR 461-155-0630(3) applies when each spouse receives SSI and
        # community-based care services, including in separate facilities.
        # Hub ruling: us-or:ssp-community-care-spouses-separate-facilities.
        couple = state_couple_total(person, period.this_year, care.astype(int)) == 2
        own_excess = max_(income - standard, 0)
        spouse_excess = (
            state_couple_total(person, period.this_year, own_excess) - own_excess
        )
        couple_payment = max_(standard - income - spouse_excess, 0)
        interim = (category == c.DISABILITY_INTERIM) | (category == c.NATURALIZATION)
        restoring_ssi = (
            (category == c.SSI_RESTORATION)
            & (ssi > 0)
            & (ssi <= federal.medical_facility)
        )
        veterans = person("veterans_benefits", period)
        restoring_va = (
            (category == c.VA_RESTORATION)
            & (veterans > 0)
            & (veterans <= p.reduced_va_pension)
        )
        suspended = (category == c.SUSPENDED_SSI) & ~receives_ssi
        diversion = max_(person("or_ssp_spousal_diversion_difference", period), 0)
        absence = category == c.ROOM_BOARD_ABSENCE
        incapacity = category == c.ROOM_BOARD_INCAPACITY
        # 461-155-0630(2)(b)(A)(iv): a temporary absence uses the income left
        # after contributing to the care liability.
        liability = max_(person("or_ssp_care_liability", period), 0)
        room_board_income = where(absence, max_(income - liability, 0), income)
        # 461-155-0250(4)(c): an OSIPM nursing facility or ICF-ID resident
        # receives the payment standard minus countable income (including
        # SSI). A $90 VA pension already exceeds it.
        # NOTE: SSI receipt stands in for OSIPM eligibility, so residents
        # without SSI whose countable income is $50 to $79.07 are not modeled.
        # The SSI medical treatment facility arrangement also includes
        # hospitals, and OSIPM-EPD residents are not excluded. A temporary
        # absence from community-based care pays only the room and board
        # payment.
        arrangement = person("ssi_federal_living_arrangement", period)
        nursing_facility = (
            arrangement == arrangement.possible_values.MEDICAL_TREATMENT_FACILITY
        ) & receives_ssi
        amount = select(
            [
                in_home,
                care & couple,
                interim | restoring_ssi | restoring_va,
                suspended | absence | incapacity,
                category == c.SPOUSAL_DIVERSION,
                nursing_facility,
            ],
            [
                p.in_home_amount,
                couple_payment,
                max_(standard - income, 0),
                max_(p.room_and_board - room_board_income, 0),
                diversion + max_(standard - income, 0),
                max_(p.nursing_facility_payment_standard - income, 0),
            ],
            default=0,
        )
        days = person("or_ssp_partial_month_days", period)
        partial_month = (days > 0) & (days < period.days)
        # 461-160-0070 uses actual calendar days and does not round the result.
        prorated = where(partial_month, amount * days / period.days, amount)
        initial = min_(
            max_(person("or_ssp_approved_initial_room_board", period), 0),
            p.room_and_board,
        )
        return where(category == c.INITIAL_ROOM_BOARD, initial, prorated)

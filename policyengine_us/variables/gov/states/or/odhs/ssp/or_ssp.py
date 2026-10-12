from policyengine_us.model_api import *


class or_ssp(Variable):
    value_type = float
    entity = Person
    label = "Oregon State Supplemental Payment"
    definition_period = MONTH
    unit = USD
    reference = (
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-155-0575.pdf",
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-155-0630.pdf",
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-155-0700.pdf",
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-160-0070.pdf",
    )
    defined_for = StateCode.OR

    def formula(person, period, parameters):
        p = parameters(period).gov.states["or"].odhs.ssp
        federal = parameters(period).gov.ssa.ssi.amount
        standard = federal.individual
        category = person("or_ssp_category", period)
        c = category.possible_values
        income = person("or_ssp_countable_income", period)
        ssi = person("ssi", period)
        in_home = (category == c.IN_HOME) & (ssi > 0) & (income == ssi)
        care = (category == c.COMMUNITY_CARE) & (ssi > 0)
        couple = person.marital_unit.sum(care) == 2
        own_excess = max_(income - standard, 0)
        spouse_excess = person.marital_unit.sum(own_excess) - own_excess
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
        suspended = (category == c.SUSPENDED_SSI) & (ssi == 0)
        diversion = max_(person("or_ssp_spousal_diversion_difference", period), 0)
        available = max_(person("or_ssp_available_room_board_income", period), 0)
        room_board = (category == c.ROOM_BOARD_ABSENCE) | (
            category == c.ROOM_BOARD_INCAPACITY
        )
        amount = select(
            [
                in_home,
                care & couple,
                interim | restoring_ssi | restoring_va,
                suspended,
                category == c.SPOUSAL_DIVERSION,
                room_board,
            ],
            [
                p.in_home_amount,
                couple_payment,
                max_(standard - income, 0),
                max_(p.room_and_board - income, 0),
                diversion + max_(standard - income, 0),
                max_(p.room_and_board - available, 0),
            ],
            default=0,
        )
        days = clip(person("or_ssp_days_eligible", period), 0, period.days)
        # 461-160-0070 uses actual calendar days and does not round the result.
        prorated = amount * days / period.days
        initial = min_(
            max_(person("or_ssp_approved_initial_room_board", period), 0),
            p.room_and_board,
        )
        return where(category == c.INITIAL_ROOM_BOARD, initial * (days > 0), prorated)

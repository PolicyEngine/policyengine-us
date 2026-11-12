from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class medicaid_optional_senior_or_disabled_income_limit(Variable):
    value_type = float
    entity = Person
    label = (
        "Income limit for a state's optional Medicaid pathway for seniors "
        "or people with disabilities"
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#m",
        "https://www.ecfr.gov/current/title-42/section-435.210",
        "https://www.law.cornell.edu/uscode/text/42/1396b#v",
        "https://www.law.cornell.edu/uscode/text/42/1382#a",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-015-00/0805-015-45-income-maximum/",
        "https://dssmanuals.mo.gov/wp-content/uploads/2022/07/mhabd-appendix-j.pdf#page=1",
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-40.310",
        "https://gc.nh.gov/rules/state_agencies/he-w800.html",
        "https://adminrules.idaho.gov/rules/current/16/160305.pdf#page=39",
        # PDF pages 10-11
        "https://humanservices.vermont.gov/sites/ahsnew/files/documents/HBEE-Part-2-Eligibility-Standards.pdf#page=10",
        "https://docs.legis.wisconsin.gov/code/admin_code/dhs/101/103/04/1/c",
        "https://www.ndlegis.gov/information/acdata/pdf/75-02-02.1.pdf#page=89",
    )

    def formula(person, period, parameters):
        # Non-MAGI Medicaid follows the SSI financial responsibility rules
        # (42 CFR 435.602): the unit is the individual, or the married
        # couple living together, whatever their filing status.
        is_couple = person.marital_unit.nb_persons() == 2
        state = person.household("state_code_str", period)
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled
        limit_pct = where(
            is_couple,
            p.income.limit.couple[state],
            p.income.limit.individual[state],
        )
        # Missouri MHABD tests eligibility based on blindness against a
        # higher share of the poverty guideline than eligibility based on
        # old age or permanent and total disability.
        mo_mhabd = parameters(period).gov.states.mo.dss.mhabd.income_limit
        is_mo = person.household("state_code", period) == StateCode.MO
        is_blind = person("is_blind", period)
        limit_pct = where(is_mo & is_blind, mo_mhabd.blind, limit_pct)
        state_group = person.household("state_group_str", period)
        unit_fpg = fpg(where(is_couple, 2, 1), state_group, period, parameters)
        # Missouri publishes monthly dollar standards (Appendix J), each the
        # percentage of the monthly guideline rounded up to the next dollar.
        mo_monthly_limit = np.ceil(limit_pct * unit_fpg / MONTHS_IN_YEAR)
        # Some states test aged, blind, and disabled people who do not
        # receive SSI against the SSI federal benefit rate itself, a monthly
        # dollar amount for an individual or a couple, rather than a share of
        # the poverty guideline (the group of 42 CFR 435.210; Louisiana pegs
        # its 42 U.S.C. 1396a(m) level to the same rate).
        # States that cover aged, blind, or disabled people only if they
        # receive SSI apply this limit to noncitizens kept in the pathway for
        # emergency Medicaid, which waives SSI receipt alone (42 U.S.C.
        # 1396b(v)(2)(B)), so they must meet SSI's income test. North
        # Dakota's 209(b) recipients also read it, and its level is SSI's
        # (N.D. Admin. Code 75-02-02.1-40(1)(a)(2)).
        ssi = parameters(period).gov.ssa.ssi.amount
        ssi_rate = where(is_couple, ssi.couple, ssi.individual) * MONTHS_IN_YEAR
        sets_ssi_rate = p.income.limit.uses_ssi_federal_benefit_rate[state].astype(bool)
        covers_group = p.covers_non_ssi_recipients[state].astype(bool)
        uses_ssi_rate = sets_ssi_rate | ~covers_group
        # Other states set a monthly dollar standard of their own: Alaska's
        # 7 AAC 40.310 standard, or the SSI rate plus the amount above it in
        # New Hampshire's standard of need (He-W 858.03(e): the minimum payment
        # level less the He-W 854.16 Medicaid standard disregard), the Vermont
        # AABD or Wisconsin state supplement, or Idaho's AABD basic allowance.
        states = parameters(period).gov.states
        ak = states.ak.dpa.ssp.income_eligibility_standard
        nh_level = states.nh.dhhs.ssp.minimum_payment_level
        vt = states.vt.dcf.aabd.amount
        wi = states.wi.dhs.ssp.amount
        disregard = p.income.disregard
        nh_amount = where(
            is_couple,
            nh_level.two_person - disregard.couple[state],
            nh_level.one_person.INDEPENDENT - disregard.individual[state],
        )
        id_amount = p.income.limit.state_standard.id
        # Each state flagged in uses_state_standard needs a branch here (or the
        # Alaska branch below); otherwise it gets the SSI rate alone.
        monthly_amount = select(
            [state == "ID", state == "NH", state == "VT", state == "WI"],
            [
                where(is_couple, id_amount.couple, id_amount.individual),
                nh_amount,
                where(is_couple, vt.couple.INDEPENDENT, vt.individual.INDEPENDENT),
                where(is_couple, wi.couple, wi.individual),
            ],
            default=0,
        )
        ak_standard = where(is_couple, ak.couple, ak.individual) * MONTHS_IN_YEAR
        state_standard = where(
            state == "AK",
            ak_standard,
            ssi_rate + monthly_amount * MONTHS_IN_YEAR,
        )
        uses_state_standard = p.income.limit.uses_state_standard[state].astype(bool)
        return select(
            [is_mo, uses_ssi_rate, uses_state_standard],
            [mo_monthly_limit * MONTHS_IN_YEAR, ssi_rate, state_standard],
            default=limit_pct * unit_fpg,
        )

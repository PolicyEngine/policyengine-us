from policyengine_us.model_api import *


class nc_sa_eligible(Variable):
    value_type = bool
    entity = Person
    label = "North Carolina Special Assistance eligibility"
    definition_period = MONTH
    defined_for = StateCode.NC
    reference = (
        "https://www.ncleg.gov/EnactedLegislation/Statutes/PDF/BySection/Chapter_108A/GS_108A-41.pdf#page=1",
        # PDF pages 6-7, 40-41, 61, 190-191, 207, 209
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-Manual-Rev-June-2026.pdf#page=6",
        # PDF pages 14, 18, 41, 48
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-In-Home-Program-Manual-Rev-June-2026.pdf#page=14",
        # 10A NCAC 71P .0603
        "http://reports.oah.state.nc.us/ncac/title%2010a%20-%20health%20and%20human%20services/chapter%2071%20-%20adult%20and%20family%20support/subchapter%20p/subchapter%20p%20rules.pdf#page=11",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.sa
        setting = person("nc_sa_care_setting", period)
        settings = setting.possible_values
        age = person("age", period.this_year)
        in_home = (setting == settings.IN_HOME) | (setting == settings.IN_HOME_ENHANCED)
        adult = age >= p.minimum_adult_age
        age_eligible = adult | (person("is_blind", period.this_year) & ~in_home)
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        # "To be eligible for SA, an individual must be eligible for SSI, or
        # ineligible for SSI solely due to being over income for SSI" (SA-3100
        # I, II.A.6). An applicant whose income would qualify for SSI must apply
        # (SA-3100 I; 10A NCAC 71P .0603(3)), and an SSI denial on other grounds
        # such as resources also denies SA (SA-3110 V.K). Income here is SSI
        # countable income, including deemed spousal income, so an applicant
        # denied SSI for spousal income qualifies (SA-5400 V).
        over_income_for_ssi = person("ssi_amount_if_eligible", period) <= person(
            "ssi_countable_income", period
        )
        # An SSI recipient automatically meets the categorical, financial and
        # resource requirements (SA-3100 II.B; SA-3200 I.A). An applicant over
        # income for SSI must meet SSI's other requirements "except for income"
        # (SA-3100 II.C), but SA tests only the applicant's own resources: "The
        # budget unit is always one" (SA-3200 I), so SSI's couple and spousal
        # resource rules do not apply. SA-3200 I and SA-3210 IV print the $2,000
        # limit and the $20 and $65 exclusions as SA's own figures; they equal
        # SSI's, so the federal parameters are used and an SSI reform carries
        # over to SA.
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period.this_year)
        immigration_status = person("immigration_status", period.this_year)
        citizen = immigration_status == immigration_status.possible_values.CITIZEN
        immigration_eligible = citizen | person(
            "is_ssi_qualified_noncitizen", period.this_year
        )
        resource_limit = parameters(
            period
        ).gov.ssa.ssi.eligibility.resources.limit.individual
        resources = person("ssi_countable_resources", period.this_year)
        non_ssi_eligible = (
            over_income_for_ssi
            & aged_blind_disabled
            & immigration_eligible
            & (resources <= resource_limit)
        )
        # "If an individual's SA payment when rounded to the nearest lower
        # whole dollar is $0.00, the individual is not eligible" (SA-3220
        # III.C). Read with III.A.4's half-up rounding, this yields the
        # published cutoffs of $1,466.51 and $1,861.51 (II.E) and applies at a
        # lower contracted rate (II.A). The monthly income test still applies
        # when the first payment is prorated without subtracting income (IV.A,
        # IV.D).
        # NOTE: G.S. 108A-41(b)(2) caps countable income at the rate plus the
        # personal needs allowance ("shall not exceed"), which would also admit
        # countable income from $0.49 below that sum up to the sum itself,
        # measured at the published rate. The two readings differ only in a
        # prorated first month, where income is not deducted. The model follows
        # the manual.
        income_eligible = person("nc_sa_full_month_amount", period) >= 1
        return (
            (setting != settings.NONE)
            & age_eligible
            & (receives_ssi | non_ssi_eligible)
            & income_eligible
            & ~person("is_incarcerated", period)
        )

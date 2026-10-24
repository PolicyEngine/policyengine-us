"""Thin Person-variable adapter for the pure supplied-record calculator."""

from datetime import date
from decimal import Decimal

import numpy as np

from policyengine_us.tools.general import has_input_for_period

from .cola import read_parameter_events
from .household import BenefitPolicies, SuppliedRecord, SurvivorBasis, calculate_year
from .parameters import bend_points_at, formula_path_at
from .pia import FormulaPath


def calculator_output(person, period, parameters, output):
    """Evaluate enabled records only, preserving ordinary public benefits.

    No calculated result is stored as a reported input. All source fields are
    explicit inputs, so a supplied zero follows the selected route unchanged.
    Source extraction can export these structural inputs without inverting a
    reformed public result. Per-call state keeps branches independent.
    """
    year = period.start.year
    sources = person("ss_calculator_source", period)
    result = np.zeros(len(sources))
    for index, source in enumerate(sources):
        if source == "off":
            continue

        def value(name, when=period):
            scalar = person("ss_calculator_" + name, when)[index]
            return scalar.item() if hasattr(scalar, "item") else scalar

        def text(name):
            return str(value(name))

        def optional_date(name):
            raw = text(name)
            return date.fromisoformat(raw) if raw else None

        def money(name, when=period):
            # Core input floats are float32. Restore the declared cents/dimes
            # before passing monthly money to the exact Decimal service.
            return Decimal(str(round(float(value(name, when)), 2)))

        kwargs = {}
        if source == "survivor":
            same_year = int(value("same_year_death_before_62"))
            if same_year not in (-1, 0, 1):
                raise ValueError("Same-year death assertion must be -1, 0 or 1")
            kwargs["survivor"] = SurvivorBasis(
                worker_birth_year=int(value("worker_birth_year")),
                death_year=int(value("death_year")),
                provenance=text("basis_provenance"),
                worker_birth_date=optional_date("worker_birth_date"),
                death_date=optional_date("death_date"),
                authoritative_year=int(value("authoritative_year")) or None,
                no_prior_disability=bool(value("no_prior_disability")),
                ordinary_non_windex=bool(value("ordinary_non_windex")),
                year_only_not_january_1=bool(value("year_only_not_january_1")),
                same_year_death_before_62=None if same_year == -1 else bool(same_year),
            )
            kwargs.update(
                monthly_amount=money("monthly_amount"),
                valuation_month=text("valuation_month"),
                composite_ratio=Decimal(text("composite_ratio")),
                ratio_description=text("ratio_description"),
                nonbinding_rib_lim=bool(value("nonbinding_rib_lim")),
                nonbinding_family_maximum=bool(value("nonbinding_family_maximum")),
                no_dual_entitlement=bool(value("no_dual_entitlement")),
                no_earnings_test_at_valuation=bool(
                    value("no_earnings_test_at_valuation")
                ),
            )
        record = SuppliedRecord(
            source=str(source),
            worker_id=text("worker_id"),
            birth_date=date.fromisoformat(text("birth_date")),
            entitlement_month=text("entitlement_month"),
            insured=bool(value("insured")),
            eligibility_year=int(value("eligibility_year")) or None,
            aime=Decimal(str(value("supplied_aime"))),
            pia=money("supplied_pia"),
            source_basis=text("source_basis"),
            supplied_claiming_factor=Decimal(text("claiming_factor"))
            if text("claiming_factor")
            else None,
            no_special_monthly_test=bool(value("no_special_monthly_test")),
            no_prior_withholding_adjustment=bool(
                value("no_prior_withholding_adjustment")
            ),
            earnings_test_no_trigger=bool(value("earnings_test_no_trigger")),
            **kwargs,
        )
        benchmark = record.benchmark()
        # Include the following January to price December entitlement, and any
        # supplied source valuation used for baseline survivor recovery.
        through = max(
            year + 1,
            int(record.valuation_month[:4]) if record.valuation_month else year,
        )
        events = read_parameter_events(parameters, through)
        earnings, before_fra, lower, higher = {}, {}, {}, {}
        paths, modes, flags = {}, {}, {}
        for payment_year in (year - 1, year, year + 1):
            if payment_year >= benchmark:
                paths[payment_year], modes[payment_year] = formula_path_at(
                    parameters, benchmark, payment_year
                )
            else:
                paths[payment_year], modes[payment_year] = FormulaPath(), "cohort"
            flags[payment_year] = (
                bool(
                    parameters.gov.contrib.congress.s770.section_2(
                        f"{payment_year}-01-01"
                    ).recompute_pre2026_death_before_eligibility
                )
                if payment_year >= 1983
                else False
            )
        for earnings_year in (year - 1, year):
            when = str(earnings_year)
            # These are dated records. Core otherwise carries an earlier pure
            # annual input forward, which would turn missing earnings into an
            # invented observation for a later earnings-test year.
            for field, destination in (
                ("annual_earnings", earnings),
                ("pre_fra_earnings", before_fra),
            ):
                if has_input_for_period(
                    person.simulation, "ss_calculator_" + field, when
                ):
                    amount = money(field, when)
                    if amount >= 0:
                        destination[earnings_year] = amount
            test = parameters.gov.ssa.social_security.earnings_test(f"{when}-01-01")
            lower[earnings_year] = test.exempt_amount_under_fra
            higher[earnings_year] = test.exempt_amount_year_of_fra
        changes, absolute_rates, withheld_years, across, payable = {}, {}, [], {}, {}
        for event in events:
            payment_year = int(event.payment_month[:4])
            if payment_year < 1983:
                continue
            policy = parameters.gov.contrib.ssa.benefit_levers.cola(
                f"{payment_year}-01-01"
            )
            if not 1 <= policy.effective_month <= 12:
                raise ValueError("COLA effective month must lie in [1, 12]")
            delta = Decimal(str(policy.pp_change))
            alternative = Decimal(str(policy.alternative_rate))
            if (
                not delta.is_finite()
                or not alternative.is_finite()
                or (alternative < 0 and alternative != -1)
            ):
                raise ValueError(
                    "COLA change must be finite; alternative rate must be nonnegative or -1"
                )
            applies = (
                event.effective_month
                >= f"{int(policy.effective_year):04d}-{int(policy.effective_month):02d}"
                if policy.effective_year
                else payment_year >= policy.start_year
            )
            applies = applies and (
                not policy.end_year or payment_year <= policy.end_year
            )
            withheld = bool(
                policy.withholding_enabled
                and has_input_for_period(
                    person.simulation,
                    "ss_calculator_withhold_cola",
                    str(payment_year),
                )
                and value("withhold_cola", str(payment_year))
            )
            changes[payment_year] = delta if applies else Decimal(0)
            if applies and alternative >= 0:
                # An absolute alternative replaces both 1999's as-paid rate
                # and its corrected rate. Ordinary baseline+delta changes
                # instead retain that historical distinction in adjusted_events.
                absolute_rates[event.payment_month] = (
                    Decimal(0) if withheld else max(Decimal(0), alternative + delta)
                )
            if withheld:
                withheld_years.append(payment_year)
        for payment_year in (year - 1, year, year + 1):
            if payment_year < 1983:
                across[payment_year], payable[payment_year] = Decimal(0), Decimal(1)
                continue
            settings = parameters.gov.contrib.ssa.benefit_levers(
                f"{payment_year}-01-01"
            )
            across[payment_year] = (
                Decimal(str(settings.across_the_board.rate))
                if payment_year >= settings.across_the_board.start_year
                else Decimal(0)
            )
            # Both supported routes are OASI, so oasi_only reaches them just
            # as a combined-OASDI payable share does.
            payable[payment_year] = Decimal(str(settings.payable.share))
        annual = calculate_year(
            record,
            year,
            bend_points=bend_points_at(parameters, benchmark),
            formula_path=paths,
            recompute_mode=modes,
            s770_survivor_bend_increase=flags,
            cola_events=events,
            policies=BenefitPolicies(
                cola_rates=absolute_rates,
                across_the_board=across,
                payable_share=payable,
                cola_pp_changes=changes,
                withheld_cola_years=tuple(withheld_years),
            ),
            earnings=earnings,
            pre_fra_earnings=before_fra,
            lower_exempt=lower,
            higher_exempt=higher,
        )
        if output in ("retirement", "survivors"):
            selected = (
                source != "survivor" if output == "retirement" else source == "survivor"
            )
            result[index] = float(annual.payment_total) if selected else 0
        elif output == "annual_entitlement":
            result[index] = float(annual.entitlement_total)
        elif output == "annual_payment":
            result[index] = float(annual.payment_total)
        elif output == "earnings_test_reduction":
            result[index] = float(annual.earnings_test_reduction)
        elif output in ("benefit", "payment", "eligibility_pia"):
            target = (
                str(period)[:7]
                if period.size == 1 and period.unit == "month"
                else f"{year}-01"
            )
            row = next(
                row
                for row in annual.ledger
                if (row.payment_month if output == "payment" else row.entitlement_month)
                == target
            )
            result[index] = float(
                row.eligibility_pia
                if output == "eligibility_pia"
                else row.payable_benefit
            )
        elif output.startswith("pia_") or output.startswith("aime_"):
            interval = (
                annual.eligibility_pia_interval
                if output.startswith("pia_")
                else annual.inferred_aime_interval
            )
            result[index] = float(interval[output.endswith("upper")]) if interval else 0
        else:
            raise ValueError(f"Unknown calculator output {output}")
    return result

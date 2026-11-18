"""S.770 scope for an identified reported survivor worker record.

This adapter reuses the supplied-record calculator's SurvivorBasis. Calculator
basis fields belong to the survivor recipient, just as on the household route;
a worker link does not authorize filling missing fields from recipient age or
combining partial bases from different people. Missing basis information leaves
the population amount unmodeled under S.770. Explicit contradictions are errors.
"""

from dataclasses import replace
from datetime import date

from policyengine_us.tools.social_security.household import (
    SurvivorBasis,
    attainment_month,
)


def survivor_formula_path(
    person, period, parameters, index, path, eligibility_year, worker_index
):
    """Return (path, unsupported) with the shared survivor bend-point reading.

    Only an active S.770 path needs these additional death/computation fields.
    Other custom formula reforms keep the caller's identified generic composite
    worker-benefit ratio route. For S.770, the same ss_calculator_* basis inputs
    used by 4a-1 must be supplied on the recipient record. Their benchmark must
    equal the independently supplied linked worker eligibility/computation year.

    The pre-2026 death-before-any-eligibility switch changes only the first
    bend-point increase. S.770's 95% first factor remains active either way.
    A worker with authoritative prior-disability eligibility receives both
    increases, as on the household route, regardless of this switch.
    """
    if not path.s770:
        return path, False
    if worker_index is None or not 0 <= int(worker_index) < len(person.ids):
        raise ValueError("Survivor worker link must identify an existing person")

    def value(name):
        scalar = person("ss_calculator_" + name, period)[index]
        return scalar.item() if hasattr(scalar, "item") else scalar

    def optional_date(name):
        raw = str(value(name))
        return date.fromisoformat(raw) if raw else None

    worker_birth_year = int(value("worker_birth_year"))
    death_year = int(value("death_year"))
    authoritative_year = int(value("authoritative_year"))
    prior_disability = int(value("prior_disability_eligibility"))
    same_year = int(value("same_year_death_before_62"))
    worker_birth_date = optional_date("worker_birth_date")
    death_date = optional_date("death_date")
    provenance = str(value("basis_provenance"))
    ordinary_non_windex = bool(value("ordinary_non_windex"))
    not_january_1 = bool(value("year_only_not_january_1"))

    if worker_birth_year < 0 or death_year < 0 or authoritative_year < 0:
        raise ValueError(
            "Survivor computation years must be positive or zero if missing"
        )
    if prior_disability not in (-1, 0, 1):
        raise ValueError("Survivor prior-disability assertion must be -1, 0 or 1")
    if same_year not in (-1, 0, 1):
        raise ValueError("Survivor same-year death assertion must be -1, 0 or 1")
    if (
        worker_birth_date
        and worker_birth_year
        and worker_birth_date.year != worker_birth_year
    ):
        raise ValueError("Worker birth date and birth year disagree")
    if death_date and death_year and death_date.year != death_year:
        raise ValueError("Death date and death year disagree")
    if death_date and worker_birth_date and death_date < worker_birth_date:
        raise ValueError("Death cannot precede birth")
    if worker_birth_year and death_year and death_year < worker_birth_year:
        raise ValueError("Death cannot precede birth")
    if death_year > period.start.year:
        raise ValueError(
            "A reported survivor's worker death cannot follow the scoring year"
        )

    # Default sentinels express unavailable information, not an assertion of a
    # complete supported basis. Do not reject ordinary population artifacts just
    # because they lack the household route's detailed scope declarations.
    if (
        not worker_birth_year
        or not death_year
        or prior_disability == -1
        or not provenance.strip()
        or not ordinary_non_windex
        or (prior_disability == 1 and not authoritative_year)
        or (not worker_birth_date and not not_january_1 and not authoritative_year)
    ):
        return path, True

    # A same-year death needs dates or the explicit assertion required by the
    # shared service. With no such observation, this is missing identification.
    year62 = (
        attainment_month(worker_birth_date, 744) // 12
        if worker_birth_date
        else worker_birth_year + 62
    )
    if (
        death_year == year62
        and not (worker_birth_date and death_date)
        and same_year == -1
    ):
        return path, True

    basis = SurvivorBasis(
        worker_birth_year=worker_birth_year,
        death_year=death_year,
        provenance=provenance,
        worker_birth_date=worker_birth_date,
        death_date=death_date,
        authoritative_year=authoritative_year or None,
        prior_disability_eligibility=bool(prior_disability),
        ordinary_non_windex=ordinary_non_windex,
        year_only_not_january_1=not_january_1,
        same_year_death_before_62=None if same_year == -1 else bool(same_year),
    )
    benchmark, before62 = basis.benchmark()
    if benchmark != int(eligibility_year):
        raise ValueError("Survivor basis and linked worker computation years disagree")

    restricted = (
        before62 and death_year < 2026 and not basis.prior_disability_eligibility
    )
    if restricted:
        increase = bool(
            parameters.gov.contrib.congress.s770.section_2(
                period.start
            ).recompute_pre2026_death_before_eligibility
        )
        return replace(path, s770_increase_first_bend_point=increase), False
    return path, False

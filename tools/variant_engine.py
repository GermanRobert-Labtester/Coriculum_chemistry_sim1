#!/usr/bin/env python3
"""N20 variant engine (Python authoring twin).

The single authoring-side generator of practice instances for the RSU MedChem
Colloquium 1 practice simulator.

Design contract (frozen for N20; see docs/VARIANT_ENGINE_FORMAT.md):

* **One authority per concern.** This module *only* generates items. It never
  scores (N17/N18/N19 own scoring), never defines a constant (N03 conventions
  own constants), and never grades. Derived values are produced here and are
  then independently recomputed through the N17 quantity engine by the review
  gate (`tools/validate_bank_review.py`).
* **Determinism.** A variant is reproducible from ``(family_id, variant_id)``
  alone: the numeric seed is derived from the family/variant seed key with
  FNV-1a 64-bit over UTF-8, and every draw comes from the N05 SplitMix64
  stream (``tools/prng.py``). Identical seeds yield byte-identical instances.
* **Cross-language parity.** All arithmetic is fixed-point integer arithmetic
  with a fixed scale, so the Python twin and the runtime twin
  (``src/variant-engine.js``) agree bit-for-bit without any transcendental
  function. No ``float`` ever reaches an emitted value.
* **No fabricated chemistry.** Parameter ranges are authored in the family
  templates; a draw outside a declared range is a hard failure, never a
  clamp. Constants come from ``data/conventions.json`` by reference only.

Usage:
    python3 tools/variant_engine.py validate --templates data/family_templates
    python3 tools/variant_engine.py instantiate --templates ... --family FAM-1C --variant A
    python3 tools/variant_engine.py emit --templates ... --bank data/bank
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prng import PrngError, SplitMix64  # noqa: E402

ENGINE_ID = 'n20-variant-engine'
ENGINE_VERSION = '1.0.0'
TEMPLATE_ISLAND_ID = 'sim-family-templates'
BANK_ISLAND_ID = 'sim-bank'
BANK_VERSION = '1.0.0-n20'
BANK_STATUS = 'frozen-reviewed-bank'

# Fixed-point scale: every numeric quantity is an integer number of 10^-SCALE
# units. Exact integer arithmetic keeps the Python and JavaScript twins
# identical without a shared floating-point contract.
SCALE = 9
SCALE_FACTOR = 10 ** SCALE

# Seed derivation: FNV-1a 64-bit over the UTF-8 bytes of the seed key.
SEED_ALGORITHM = 'fnv1a64-utf8-v1'
FNV_OFFSET = 0xCBF29CE484222325
FNV_PRIME = 0x100000001B3
MASK_64 = 0xFFFFFFFFFFFFFFFF

# The set of response types the schema declares.
TYPE_IDS = tuple(f'Q{i:02d}' for i in range(1, 19))
PAYLOAD_CLASSES = ('numeric', 'option_select', 'ordering', 'matching', 'graph', 'method')

# Recipe operations. Every operation is exact integer arithmetic on the
# fixed-point representation (or an exact rational that is rounded once, with
# a documented half-away-from-zero rule).
RECIPE_OPS = ('identity', 'add', 'sub', 'mul', 'div', 'mul_div', 'lin', 'pow_int', 'percent',
             'negate', 'log10_pow10', 'round_decimals')


class VariantEngineError(ValueError):
    """Named failure of the variant engine (honest failure by name)."""

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(f'[{code}] {message}')
        self.code = code
        self.message = message
        self.details = details or {}


# --------------------------------------------------------- conventions refs

def resolve_convention(conventions: dict[str, Any], ref: str) -> str:
    """Resolve a conventions reference to its numeric string.

    Supported reference forms:
      ``molar_mass:<formula>``   compound molar mass (working value)
      ``atomic_mass:<symbol>``   relative atomic mass
      ``constant:<id>``           a named constant (N_A, R, F, ...)
      ``potential:<id>``         a reference standard potential
      ``nernst_slope``            the Nernst slope declared in the potentials section
      ``conversion:<id>:num`` / ``conversion:<id>:den``  a unit-conversion factor
    """
    kind, _, rest = ref.partition(':')
    if kind == 'molar_mass':
        for entry in conventions['compound_molar_masses']['compounds']:
            if entry.get('formula') == rest:
                return str(entry.get('working_value') or entry.get('value'))
    elif kind == 'atomic_mass':
        for entry in conventions['atomic_masses']['elements']:
            if entry.get('symbol') == rest:
                return str(entry.get('value'))
    elif kind == 'constant':
        for entry in conventions['constants']['values']:
            if entry.get('id') == rest:
                return str(entry.get('value'))
    elif kind == 'potential':
        for entry in conventions['potentials']['reference_values']:
            if entry.get('id') == rest:
                return str(entry.get('value'))
    elif kind == 'nernst_slope':
        return str(conventions['potentials']['nernst']['slope_V'])
    elif kind == 'conversion':
        parts = rest.split(':')
        cid = parts[0]
        which = parts[1] if len(parts) > 1 else 'num'
        for entry in conventions['unit_system']['conversions']:
            if entry.get('id') == cid:
                factor = entry.get('factor') or {}
                if which in ('num', 'den'):
                    return str(factor[which])
    raise VariantEngineError('E_VAR_CONVENTION_REF',
                             f'Konvenciju atsauce neatris: {ref!r}.')


# --------------------------------------------------------------------- numbers

class Num:
    """A JSON number emitted verbatim.

    Keeping the literal text (instead of a float) guarantees that the Python
    twin, the JavaScript twin and the emitted instance file agree byte for
    byte, and that a value never silently changes shape through a float
    round-trip.
    """

    __slots__ = ('text', 'value')

    def __init__(self, text: str, value: int) -> None:
        self.text = text
        self.value = value  # fixed-point integer

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f'Num({self.text!r})'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Num) and other.text == self.text

    def __hash__(self) -> int:
        return hash(self.text)


def half_up_div(num: int, den: int) -> int:
    """Integer division rounded half away from zero (Python and JS identical)."""
    if den == 0:
        raise VariantEngineError('E_VAR_DIV_ZERO', 'Receptes dalījums ar nulli.')
    if den < 0:
        num, den = -num, -den
    sign = -1 if num < 0 else 1
    mag = abs(num)
    quotient = (2 * mag + den) // (2 * den)
    return sign * quotient


def fixed_from_scaled(scaled: int, decimals: int) -> int:
    """Convert an integer expressed in 10^-decimals units to the fixed-point scale."""
    if decimals > SCALE:
        raise VariantEngineError(
            'E_VAR_SCALE', f'Parametra decimāldašas ({decimals}) pārsniedz fiksēto punktu skalu ({SCALE}).')
    return scaled * (10 ** (SCALE - decimals))


def fixed_to_decimal_text(value: int, decimals: int) -> str:
    """Render a fixed-point integer as a plain decimal string with ``decimals`` digits."""
    if decimals < 0:
        raise VariantEngineError('E_VAR_SCALE', 'Decimāldašu skaits nevar būt negatīvs.')
    neg = value < 0
    mag = abs(value)
    divisor = 10 ** decimals
    whole, frac = divmod(mag, divisor)
    text = f'{whole}.{frac:0{decimals}d}' if decimals else str(whole)
    return f'-{text}' if neg else text


def num_literal(value: int) -> Num:
    """Canonical JSON number literal for a fixed-point integer (trailing zeros trimmed)."""
    text = fixed_to_decimal_text(value, SCALE)
    if '.' in text:
        text = text.rstrip('0').rstrip('.')
        if text in ('', '-'):
            text = '0'
        if text == '-0':
            text = '0'
    return Num(text, value)


def _digit_count(value: int) -> int:
    """Number of decimal digits of |value|."""
    if value == 0:
        return 1
    return len(str(abs(value)))


def written_sig_figs(text: str) -> int:
    """Significant figures of a *written* number, by the N17 rule.

    N17 counts the digits of a written mantissa: with a decimal point every
    digit counts, without one the trailing zeros are ambiguous and do not
    count. The answer's written form is what a learner types and what the
    grader counts, so the engine has to know the count of the form it emits.
    A scientific form ("6,80 × 10²") is counted on its mantissa, and the
    Latvian decimal separator is normalised to a dot first, exactly as N17's
    parser does.
    """
    raw = str(text).strip()
    match = re.match(r'^([+-]?[0-9]+(?:[.,][0-9]*)?)\s*(?:[×x*]\s*10)', raw)
    mantissa = match.group(1) if match else raw.split(' ')[0]
    mantissa = mantissa.replace(',', '.')
    if '.' in mantissa:
        digits = mantissa.replace('.', '').lstrip('0')
        return len(digits) if digits else 1
    digits = mantissa.lstrip('0').rstrip('0')
    return len(digits) if digits else 1


SUPERSCRIPT = str.maketrans('0123456789-+', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺')


def scientific_text(value: int, sig: int) -> str:
    """The answer in scientific notation, e.g. 680 at 3 significant figures.

    A whole number whose significant figures live in trailing zeros (``680``)
    cannot carry them in plain notation: N17 counts ``680`` as two
    significant figures. ``6,80 × 10²`` carries three, and N17 parses it.
    """
    if value == 0:
        raise VariantEngineError('E_VAR_ZERO', 'Nulle nevar būt zinātniski rakstīts.')
    negative = value < 0
    magnitude = -value if negative else value
    exponent = _digit_count(magnitude) - 1 - SCALE
    if exponent >= 0:
        mantissa = magnitude // (10 ** exponent)
    else:
        mantissa = magnitude * (10 ** (-exponent))
    decimals = max(0, sig - 1)
    text = _format_latvian(mantissa, decimals)
    exponent_text = str(exponent).translate(SUPERSCRIPT)
    return f"{'-' if negative else ''}{text} × 10{exponent_text}"


def round_to_sig_figs(value: int, sig: int) -> int:
    """Round a fixed-point integer to ``sig`` significant figures, half away from zero.

    The rounding rule itself belongs to the conventions (``rounding.mode =
    half_up``) and is implemented by the N17 quantity engine; this integer
    version exists so that the Python and JavaScript twins emit identical
    bytes without a shared float contract. The review gate proves the two
    agree on every numeric instance in the bank.
    """
    if sig < 1:
        raise VariantEngineError('E_VAR_SCALE', 'Zīmīgo ciparu skaitam jābūt vismaz 1.')
    if value == 0:
        return 0
    digits = _digit_count(value)
    if digits <= sig:
        return value
    quantum = 10 ** (digits - sig)
    quotient, remainder = divmod(abs(value), quantum)
    if remainder * 2 >= quantum:
        quotient += 1
    result = quotient * quantum
    return -result if value < 0 else result


def sig_fig_decimals(value: int, sig: int) -> int:
    """Decimal places that make the written form carry ``sig`` significant figures.

    ``794`` needs no decimals, ``0,25`` needs three (``0,250``). The written
    form is what the N17 engine counts significant figures from, so the answer
    display has to keep the declared precision.
    """
    if value == 0:
        return max(0, sig - 1)
    integer_digits = max(0, _digit_count(value) - SCALE)
    return max(0, sig - integer_digits)


def round_to_decimals(value: int, decimals: int) -> int:
    """Round a fixed-point integer to ``decimals`` decimal places, half away from zero.

    Reading items (a burette, a measuring cylinder) are reported to a fixed
    number of decimals rather than to a number of significant figures, so the
    payload declares the rounding mode explicitly.
    """
    if decimals < 0 or decimals > SCALE:
        raise VariantEngineError('E_VAR_SCALE', f'Decimāldašu skaits ārpus 0..{SCALE}.')
    quantum = 10 ** (SCALE - decimals)
    quotient, remainder = divmod(abs(value), quantum)
    if remainder * 2 >= quantum:
        quotient += 1
    result = quotient * quantum
    return -result if value < 0 else result


def round_answer(value: int, mode: str, digits: int) -> tuple[int, int]:
    """Round a computed answer and report the decimals its written form needs.

    Returns the rounded fixed-point value and the number of decimal places the
    display must use. ``significant_figures`` follows the conventions' half-up
    rule on the significant digits; ``decimal_places`` follows the instrument's
    reported precision.
    """
    if mode == 'decimal_places':
        rounded = round_to_decimals(value, digits)
        return rounded, digits
    rounded = round_to_sig_figs(value, digits)
    return rounded, sig_fig_decimals(rounded, digits)


def fixed_to_float(value: int) -> float:
    return value / SCALE_FACTOR


# ----------------------------------------------------------------- canonical IO

def exact_number_text(value: float) -> str:
    """Exact decimal text for a JSON number that is not an integer.

    The canonical writer must produce the same bytes in Python and in
    JavaScript. Both languages use the shortest round-trip representation of a
    double, so the two agree for the magnitudes a question bank uses; the
    guards below make a disagreement impossible to hide by refusing an
    exponent form or an excessive number of decimals.
    """
    import decimal
    if value != value or value in (float('inf'), float('-inf')):
        raise VariantEngineError('E_VAR_FLOAT', 'Nav pieņemama skaitļa vērtība.')
    if value == int(value):
        return str(int(value))
    dec = decimal.Decimal(repr(value))
    sign, digits, exponent = dec.as_tuple()
    if exponent < -SCALE:
        raise VariantEngineError('E_VAR_FLOAT',
                                 f'Skaitlis {value!r} vajag vairāk nekā {SCALE} decimāldašu.')
    text = format(dec, 'f')
    return text


def canonical_bytes(value: Any) -> bytes:
    """Canonical JSON bytes: sorted keys, no whitespace, UTF-8, verbatim numbers."""
    out: list[str] = []
    _write_canonical(value, out)
    return ''.join(out).encode('utf-8')


def _write_canonical(value: Any, out: list[str]) -> None:
    if isinstance(value, Num):
        out.append(value.text)
    elif value is True:
        out.append('true')
    elif value is False:
        out.append('false')
    elif value is None:
        out.append('null')
    elif isinstance(value, int):
        out.append(str(value))
    elif isinstance(value, float):
        # Floats reach the writer only for genuinely fractional point values;
        # the exact decimal text keeps the Python and JavaScript twins
        # byte-identical.
        out.append(exact_number_text(value))
    elif isinstance(value, str):
        out.append(json.dumps(value, ensure_ascii=False))
    elif isinstance(value, (list, tuple)):
        out.append('[')
        for index, item in enumerate(value):
            if index:
                out.append(',')
            _write_canonical(item, out)
        out.append(']')
    elif isinstance(value, dict):
        out.append('{')
        for index, key in enumerate(sorted(value.keys())):
            if index:
                out.append(',')
            out.append(json.dumps(str(key), ensure_ascii=False))
            out.append(':')
            _write_canonical(value[key], out)
        out.append('}')
    else:
        raise VariantEngineError('E_VAR_TYPE', f'Nepazīstams tips emitējamai vērtībai: {type(value).__name__}')


def sha256_bytes(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def digest_of(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


# ------------------------------------------------------------------ seed rules

def derive_seed(seed_key: str) -> int:
    """Derive the numeric PRNG seed from a family/variant seed key."""
    if not isinstance(seed_key, str) or not seed_key.strip():
        raise VariantEngineError('E_VAR_SEED_KEY', 'Seed key must be a non-empty string.')
    digest = FNV_OFFSET
    for byte in seed_key.encode('utf-8'):
        digest ^= byte
        digest = (digest * FNV_PRIME) & MASK_64
    if digest == 0:
        digest = 1
    return digest


def ephemeral_seed(family_id: str, variant_id: str, attempt: int,
                   frozen_seeds: Iterable[int] | None = None) -> tuple[int, int]:
    """Pick an ephemeral retry seed that never collides with a frozen seed.

    The candidate key is ``{family}-{variant}-EPH-{attempt}``. When the derived
    seed is already used by the frozen bank, the attempt counter advances until
    an unused seed is found. The rule is total, deterministic and documented.
    """
    frozen = set(frozen_seeds or ())
    counter = attempt
    while True:
        seed = derive_seed(f'{family_id}-{variant_id}-EPH-{counter}')
        if seed not in frozen:
            return seed, counter
        counter += 1
        if counter > attempt + 10_000:
            raise VariantEngineError('E_VAR_SEED_EXHAUSTED', 'Neatrasta brīva pagaidu sēkla.')


# ----------------------------------------------------------------- recipe eval

def eval_recipe(op: str, args: Sequence[int]) -> int:
    """Evaluate one recipe operation on fixed-point integers."""
    if op == 'identity':
        if len(args) != 1:
            raise VariantEngineError('E_VAR_RECIPE', 'identity requires 1 argument.')
        return args[0]
    if op == 'add':
        if len(args) != 2:
            raise VariantEngineError('E_VAR_RECIPE', 'add requires 2 arguments.')
        return args[0] + args[1]
    if op == 'sub':
        if len(args) != 2:
            raise VariantEngineError('E_VAR_RECIPE', 'sub requires 2 arguments.')
        return args[0] - args[1]
    if op == 'mul':
        if len(args) != 2:
            raise VariantEngineError('E_VAR_RECIPE', 'mul requires 2 arguments.')
        return half_up_div(args[0] * args[1], SCALE_FACTOR)
    if op == 'div':
        if len(args) != 2:
            raise VariantEngineError('E_VAR_RECIPE', 'div requires 2 arguments.')
        return half_up_div(args[0] * SCALE_FACTOR, args[1])
    if op == 'mul_div':
        if len(args) != 3:
            raise VariantEngineError('E_VAR_RECIPE', 'mul_div requires 3 arguments.')
        return half_up_div(args[0] * args[1], args[2])
    if op == 'lin':
        if len(args) != 3:
            raise VariantEngineError('E_VAR_RECIPE', 'lin requires 3 arguments.')
        return half_up_div(args[0] * args[1], SCALE_FACTOR) + args[2]
    if op == 'pow_int':
        if len(args) != 2:
            raise VariantEngineError('E_VAR_RECIPE', 'pow_int requires 2 arguments.')
        base, exponent = args
        if exponent < 0:
            raise VariantEngineError('E_VAR_RECIPE', 'pow_int requires a non-negative exponent.')
        result = SCALE_FACTOR
        for _ in range(exponent):
            result = half_up_div(result * base, SCALE_FACTOR)
        return result
    if op == 'percent':
        if len(args) != 2:
            raise VariantEngineError('E_VAR_RECIPE', 'percent requires 2 arguments.')
        return half_up_div(args[0] * 100 * SCALE_FACTOR, args[1])
    if op == 'negate':
        if len(args) != 1:
            raise VariantEngineError('E_VAR_RECIPE', 'negate requires 1 argument.')
        return -args[0]
    if op == 'log10_pow10':
        if len(args) != 1:
            raise VariantEngineError('E_VAR_RECIPE', 'log10_pow10 requires 1 argument.')
        return log10_pow10(args[0])
    if op == 'round_decimals':
        if len(args) != 2:
            raise VariantEngineError('E_VAR_RECIPE', 'round_decimals requires 2 arguments.')
        digits, remainder = divmod(abs(args[1]), SCALE_FACTOR)
        if remainder:
            raise VariantEngineError('E_VAR_RECIPE',
                                     'round_decimals requires a whole decimal count.')
        return round_to_decimals(args[0], int(digits))
    raise VariantEngineError('E_VAR_RECIPE', f'Nezināma receptes operācija: {op!r}')


def log10_pow10(value: int) -> int:
    """Exact decimal logarithm of an exact power of ten (>= 1).

    The operation is integer arithmetic only: the number of trailing decimal
    zeros of the fixed-point representation is counted, so no transcendental
    function is involved and the two language twins cannot drift. A value that
    is not an exact power of ten is a hard failure, never an approximation.
    """
    if value <= 0:
        raise VariantEngineError('E_VAR_RECIPE', 'log10_pow10 requires a positive value.')
    magnitude = value
    zeros = 0
    while magnitude % 10 == 0:
        magnitude //= 10
        zeros += 1
    if magnitude != 1:
        raise VariantEngineError('E_VAR_RECIPE',
                                 'log10_pow10 requires an exact power of ten.')
    exponent = zeros - SCALE
    if exponent < 0:
        raise VariantEngineError('E_VAR_RECIPE', 'log10_pow10 requires a value >= 1.')
    return exponent * SCALE_FACTOR


# ------------------------------------------------------------------- templates

def load_templates(template_dir: Path) -> list[dict[str, Any]]:
    """Load and merge the family template files in family order."""
    files = sorted(p for p in Path(template_dir).rglob('*.json') if p.is_file())
    families: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in files:
        raw = json.loads(path.read_text(encoding='utf-8'))
        if raw.get('island_id') != TEMPLATE_ISLAND_ID:
            raise VariantEngineError(
                'E_VAR_TEMPLATE_ISLAND',
                f'Template fails {path} declares island_id {raw.get("island_id")!r}.')
        for family in raw.get('families', []):
            family_id = family.get('family_id')
            if family_id in seen:
                raise VariantEngineError('E_VAR_TEMPLATE_DUP', f'Dubultā ģimeņa deklarācija: {family_id}.')
            seen.add(family_id)
            family['_source_file'] = str(path)
            families.append(family)
    families.sort(key=lambda f: f['family_id'])
    return families


def template_digest(templates: Sequence[dict[str, Any]]) -> str:
    payload = []
    for family in templates:
        clean = {k: v for k, v in family.items() if not k.startswith('_')}
        payload.append(clean)
    return digest_of(payload)


# ------------------------------------------------------------------ validation

def _violation(code: str, family_id: str, field: str, message: str) -> dict[str, Any]:
    return {'code': code, 'family_id': family_id, 'field': field, 'message': message}


def validate_templates(templates: Sequence[dict[str, Any]], repo_root: Path,
                       conventions: dict[str, Any] | None = None) -> dict[str, Any]:
    """Validate the family templates against the schema, conventions and contracts.

    Checks performed per family:
      * the family id matches the N04 family pattern and the topic digit;
      * every response type exists in the N04 schema and the payload class of
        the variant matches the schema's type-to-payload map;
      * every parameter range is well formed and inside the declared range;
      * every conventions reference resolves inside ``data/conventions.json``;
      * every derived recipe resolves and every answer role has a tolerance
        class that resolves in the conventions island;
      * the rubric points sum to the family point weight;
      * required per-form types are covered across the template set.
    """
    schema = json.loads((repo_root / 'data/question_schema.json').read_text(encoding='utf-8'))
    type_payload = {tid: spec['payload_class'] for tid, spec in schema['types'].items()}
    required_types = list(schema['required_types_per_form'])
    if conventions is None:
        conventions = json.loads((repo_root / 'data/conventions.json').read_text(encoding='utf-8'))
    tolerance_classes = {q['id'] for q in conventions['tolerances']['quantity_classes']}

    violations: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    covered_types: set[str] = set()

    for family in templates:
        family_id = family.get('family_id', '<unknown>')
        if not isinstance(family_id, str) or len(family_id) != 6 or not family_id.startswith('FAM-'):
            violations.append(_violation('E_VAR_FAMILY_ID', family_id, 'family_id',
                                         'family_id must match FAM-[1-7][A-D].'))
        topic = family.get('topic')
        if not isinstance(topic, int) or not (1 <= topic <= 7):
            violations.append(_violation('E_VAR_TOPIC', family_id, 'topic', 'Topic must be an integer 1..7.'))
        elif family_id[4] != str(topic):
            violations.append(_violation('E_VAR_TOPIC', family_id, 'topic',
                                         f'family_id topic digit {family_id[4]} != topic {topic}.'))
        weight = family.get('point_weight')
        if not isinstance(weight, (int, float)) or weight <= 0:
            violations.append(_violation('E_VAR_WEIGHT', family_id, 'point_weight',
                                         'point_weight must be a positive number (PROPOSED training policy).'))

        variants = family.get('variants') or []
        if len(variants) != 4:
            violations.append(_violation('E_VAR_VARIANT_COUNT', family_id, 'variants',
                                         f'Family must declare 4 variants, found {len(variants)}.'))
        variant_ids = [v.get('variant_id') for v in variants]
        if sorted(variant_ids) != ['A', 'B', 'C', 'D']:
            violations.append(_violation('E_VAR_VARIANT_IDS', family_id, 'variants',
                                         f'Variant ids must be A..D, found {variant_ids}.'))
        type_mix = set(family.get('type_mix') or [])
        rubric_sum = 0.0
        for variant in variants:
            vid = variant.get('variant_id', '?')
            field = f'variants[{vid}]'
            type_id = variant.get('type_id')
            if type_id not in TYPE_IDS:
                violations.append(_violation('E_VAR_TYPE', family_id, field,
                                             f'Unknown response type {type_id!r}.'))
            else:
                covered_types.add(type_id)
                if type_id not in type_mix:
                    violations.append(_violation('E_VAR_TYPE_MIX', family_id, field,
                                                 f'Type {type_id} is not part of the family type mix.'))
                expected_class = type_payload[type_id]
                payload = variant.get('payload') or {}
                if payload.get('class') != expected_class:
                    violations.append(_violation('E_VAR_PAYLOAD_CLASS', family_id, field,
                                                 f'payload.class {payload.get("class")!r} != {expected_class!r}.'))
            rubric = variant.get('rubric') or []
            if not rubric:
                violations.append(_violation('E_VAR_RUBRIC', family_id, field, 'Rubric must not be empty.'))
            points = sum(float(r.get('points', 0)) for r in rubric)
            rubric_sum = points
            if isinstance(weight, (int, float)) and abs(points - float(weight)) > 1e-9:
                violations.append(_violation('E_VAR_RUBRIC_POINTS', family_id, field,
                                             f'Rubric points {points} != family point_weight {weight}.'))
            for param in variant.get('parameters') or []:
                _validate_parameter(param, family_id, field, violations)
            values: set[str] = set()
            known_ids = {p['param_id'] for p in variant.get('parameters') or []}
            for derived in variant.get('derived') or []:
                _validate_derived(derived, family_id, field, values, tolerance_classes, violations)
                if derived.get('kind') in ('constant', 'fixed'):
                    _validate_parameter(derived, family_id, field, violations)
                    known_ids.add(derived['param_id'])
                else:
                    known_ids.add(derived.get('value_id'))
            for derived in variant.get('derived') or []:
                if derived.get('kind') in ('constant', 'fixed'):
                    continue
                for arg in derived.get('args') or []:
                    if arg not in known_ids:
                        violations.append(_violation(
                            'E_VAR_RECIPE_ARGS', family_id, f'{field}.{derived.get("value_id")}',
                            f'Recipe argument {arg!r} is not a declared value of this variant.'))
            for answer in variant.get('answers') or []:
                if answer.get('tolerance_class') not in tolerance_classes:
                    violations.append(_violation('E_VAR_TOLERANCE', family_id, field,
                                                 f'tolerance_class {answer.get("tolerance_class")!r} does not resolve in #sim-conventions.'))
        if isinstance(weight, (int, float)) and abs(rubric_sum - float(weight)) > 1e-9:
            violations.append(_violation('E_VAR_RUBRIC_POINTS', family_id, 'variants',
                                         f'Variant rubric points {rubric_sum} != family point_weight {weight}.'))
        rows.append({
            'family_id': family_id,
            'topic': topic,
            'point_weight': weight,
            'types': sorted({v.get('type_id') for v in variants if v.get('type_id')}),
            'variants': len(variants),
            'parameters': sum(len(v.get('parameters') or []) for v in variants),
            'derived_values': sum(len(v.get('derived') or []) for v in variants),
            'source_file': family.get('_source_file'),
        })

    missing_required = [t for t in required_types if t not in covered_types]
    if missing_required:
        violations.append(_violation('E_VAR_REQUIRED_TYPES', '<set>', 'required_types_per_form',
                                     f'Template set does not cover required types {missing_required}.'))

    return {
        'status': 'PASS' if not violations else 'FAIL',
        'families': len(templates),
        'rows': rows,
        'required_types_covered': sorted(covered_types & set(required_types)),
        'required_types_missing': missing_required,
        'violations': violations,
    }


def _validate_parameter(param: dict[str, Any], family_id: str, field: str,
                        violations: list[dict[str, Any]]) -> None:
    pid = param.get('param_id', '<missing>')
    kind = param.get('kind')
    if kind not in ('int', 'choice', 'constant', 'fixed'):
        violations.append(_violation('E_VAR_PARAM_KIND', family_id, f'{field}.{pid}',
                                     f'Parameter kind must be "int", "choice", "constant" or '
                                     f'"fixed", got {kind!r}.'))
        return
    if kind == 'constant':
        ref = param.get('conventions_ref')
        if not isinstance(ref, str) or not ref:
            violations.append(_violation('E_VAR_PARAM_SHAPE', family_id, f'{field}.{pid}',
                                         'A constant parameter needs a conventions_ref.'))
        if not isinstance(param.get('decimals'), int):
            violations.append(_violation('E_VAR_PARAM_SHAPE', family_id, f'{field}.{pid}',
                                         'A constant parameter needs an integer decimals.'))
        return
    if kind == 'fixed':
        if not isinstance(param.get('value'), int):
            violations.append(_violation('E_VAR_PARAM_SHAPE', family_id, f'{field}.{pid}',
                                         'A fixed parameter needs an integer value.'))
        if not isinstance(param.get('decimals'), int):
            violations.append(_violation('E_VAR_PARAM_SHAPE', family_id, f'{field}.{pid}',
                                         'A fixed parameter needs an integer decimals.'))
        if not isinstance(param.get('note_lv'), str) or not param['note_lv'].strip():
            violations.append(_violation('E_VAR_PARAM_SHAPE', family_id, f'{field}.{pid}',
                                         'A fixed parameter needs a note_lv naming its origin.'))
        return
    if kind == 'choice':
        choices = param.get('choices') or []
        if len(choices) < 2:
            violations.append(_violation('E_VAR_PARAM_CHOICES', family_id, f'{field}.{pid}',
                                         'A choice parameter needs at least two choices.'))
        return
    for key in ('min', 'max', 'step', 'decimals'):
        if not isinstance(param.get(key), int):
            violations.append(_violation('E_VAR_PARAM_SHAPE', family_id, f'{field}.{pid}',
                                         f'Parameter {key} must be an integer.'))
            return
    if param['min'] > param['max']:
        violations.append(_violation('E_VAR_PARAM_RANGE', family_id, f'{field}.{pid}',
                                     f'Parameter min {param["min"]} > max {param["max"]}.'))
    if param['step'] <= 0:
        violations.append(_violation('E_VAR_PARAM_RANGE', family_id, f'{field}.{pid}',
                                     'Parameter step must be positive.'))
    if (param['max'] - param['min']) % param['step'] != 0:
        violations.append(_violation('E_VAR_PARAM_RANGE', family_id, f'{field}.{pid}',
                                     'Parameter range is not divisible by its step.'))
    if param['decimals'] < 0 or param['decimals'] > SCALE:
        violations.append(_violation('E_VAR_PARAM_SHAPE', family_id, f'{field}.{pid}',
                                     f'Parameter decimals {param["decimals"]} outside 0..{SCALE}.'))


def _validate_derived(derived: dict[str, Any], family_id: str, field: str,
                      values: set[str], tolerance_classes: set[str],
                      violations: list[dict[str, Any]]) -> None:
    if derived.get('kind') in ('constant', 'fixed'):
        # A specification with kind ``constant`` or ``fixed`` is an *input*
        # that happens to be declared among the derived values; it carries no
        # recipe and no value_id, and is validated by ``_validate_parameter``.
        if not isinstance(derived.get('param_id'), str) or not derived['param_id']:
            violations.append(_violation('E_VAR_VALUE_ID', family_id, f'{field}.<constant>',
                                         'A constant/fixed specification needs a param_id.'))
        return
    vid = derived.get('value_id', '<missing>')
    if not isinstance(vid, str) or not vid:
        violations.append(_violation('E_VAR_VALUE_ID', family_id, f'{field}.{vid}',
                                     'Derived value needs a value_id.'))
        return
    if vid in values:
        violations.append(_violation('E_VAR_VALUE_ID', family_id, f'{field}.{vid}',
                                     'Duplicate value_id inside a variant.'))
    values.add(vid)
    op = derived.get('op')
    if op not in RECIPE_OPS:
        violations.append(_violation('E_VAR_RECIPE_OP', family_id, f'{field}.{vid}',
                                     f'Unknown recipe op {op!r}.'))
    if not isinstance(derived.get('args'), list) or not derived.get('args'):
        violations.append(_violation('E_VAR_RECIPE_ARGS', family_id, f'{field}.{vid}',
                                     'Derived value needs a non-empty args list.'))
    if derived.get('role') == 'answer' and derived.get('tolerance_class') not in tolerance_classes:
        violations.append(_violation('E_VAR_TOLERANCE', family_id, f'{field}.{vid}',
                                     f'Answer tolerance_class {derived.get("tolerance_class")!r} does not resolve.'))


# ---------------------------------------------------------------- instantiation

def variant_inputs(variant: dict[str, Any]) -> list[dict[str, Any]]:
    """Ordered, non-drawn inputs of a variant.

    Parameters and any constant/fixed specification found inside the derived
    list share one namespace: a specification with kind ``constant`` or
    ``fixed`` is an input even when it is declared among the derived values.
    """
    inputs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for spec in list(variant.get('parameters') or []):
        pid = spec['param_id']
        if pid in seen:
            raise VariantEngineError('E_VAR_DUPLICATE_INPUT', f'Dubultā ievades deklarācija: {pid}.')
        seen.add(pid)
        inputs.append(spec)
    for spec in variant.get('derived') or []:
        if spec.get('kind') not in ('constant', 'fixed'):
            continue
        pid = spec['param_id']
        if pid in seen:
            raise VariantEngineError('E_VAR_DUPLICATE_INPUT', f'Dubultā ievades deklarācija: {pid}.')
        seen.add(pid)
        inputs.append(spec)
    return inputs


def variant_derived(variant: dict[str, Any]) -> list[dict[str, Any]]:
    return [d for d in variant.get('derived') or [] if d.get('kind') not in ('constant', 'fixed')]


def _resolve_inputs(conventions: dict[str, Any], variant: dict[str, Any]) -> dict[str, int]:
    """Resolve the non-drawn inputs (conventions constants and fixed factors)."""
    from decimal import Decimal
    resolved: dict[str, int] = {}
    for spec in variant_inputs(variant):
        kind = spec.get('kind')
        pid = spec['param_id']
        if kind == 'constant':
            raw = resolve_convention(conventions, spec['conventions_ref'])
            decimals = int(spec.get('decimals', 0))
            value = Decimal(str(raw))
            scaled = int((value * (Decimal(10) ** decimals)).to_integral_value())
            resolved[pid] = fixed_from_scaled(scaled, decimals)
        elif kind == 'fixed':
            resolved[pid] = fixed_from_scaled(int(spec['value']), int(spec.get('decimals', 0)))
    return resolved


def _draw_parameters(prng: SplitMix64, variant: dict[str, Any]) -> dict[str, int]:
    drawn: dict[str, int] = {}
    for param in variant_inputs(variant):
        pid = param['param_id']
        if param['kind'] == 'choice':
            choices = param['choices']
            index = prng.next_int(len(choices))
            drawn[pid] = index
            continue
        if param['kind'] != 'int':
            continue
        span = (param['max'] - param['min']) // param['step']
        index = prng.next_int(span + 1)
        scaled = param['min'] + index * param['step']
        drawn[pid] = fixed_from_scaled(scaled, param['decimals'])
    return drawn


def _compute_derived(variant: dict[str, Any], values: dict[str, int]) -> dict[str, int]:
    computed = dict(values)
    for derived in variant_derived(variant):
        op = derived['op']
        args = [computed[arg] for arg in derived['args']]
        computed[derived['value_id']] = eval_recipe(op, args)
    return computed


def _format_latvian(value: int, decimals: int) -> str:
    """Render a fixed-point integer with ``decimals`` decimal places.

    The stored integer is always in units of 10^-SCALE; ``decimals`` is the
    *display* precision and therefore rounds (half away from zero) before the
    text is written. Rendering at the wrong scale is a silent corruption of
    every number a learner sees, so the conversion lives in one place.
    """
    if decimals < 0 or decimals > SCALE:
        raise VariantEngineError('E_VAR_SCALE', f'Attēlotā decimāldašu skaita diapazons: 0..{SCALE}.')
    neg = value < 0
    mag = -value if neg else value
    factor = 10 ** (SCALE - decimals)
    quotient, remainder = divmod(mag, factor)
    if remainder * 2 >= factor:
        quotient += 1
    whole, frac = divmod(quotient, 10 ** decimals)
    text = f'{whole}.{frac:0{decimals}d}' if decimals else str(whole)
    # Latvian writes the decimal separator as a comma. The JavaScript twin
    # writes the same comma, and the two must agree byte for byte, so the
    # separator is fixed here rather than at each call site.
    text = text.replace('.', ',')
    return f'-{text}' if neg else text


def _render_text(text: str, values: dict[str, int], decimals: dict[str, int],
                 overrides: dict[str, str] | None = None) -> str:
    out = str(text)
    for key, dec in decimals.items():
        if '{' + key + '}' in out:
            if overrides and key in overrides:
                out = out.replace('{' + key + '}', overrides[key])
            else:
                out = out.replace('{' + key + '}', _format_latvian(values[key], dec))
    return out


def _rubric_points(variant: dict[str, Any]) -> float:
    return sum(float(r.get('points', 0)) for r in variant.get('rubric') or [])


def _draw_record(param: dict[str, Any], computed: dict[str, int],
                 text_of: Any) -> dict[str, Any]:
    """One drawn-input record for the instance's audit table.

    The record is deliberately compact: it names the parameter, its kind, its
    learner-facing label and the value that was drawn. A constant additionally
    names the conventions entry it was resolved from, because that reference
    is the authority for the number and must stay traceable inside the frozen
    bank. Units and the authoring note live in the family template and in the
    recompute record; repeating them in all 112 instances would spend the
    bank's byte budget on duplication.
    """
    if param['kind'] == 'choice':
        value = param['choices'][computed[param['param_id']]]
    else:
        value = text_of(param['param_id'])
    record: dict[str, Any] = {
        'param_id': param['param_id'],
        'kind': param['kind'],
        'label_lv': param.get('label_lv'),
        'value': value,
    }
    if param['kind'] == 'constant':
        record['source'] = param.get('conventions_ref')
    return record


def instantiate(template: dict[str, Any], variant: dict[str, Any],
                seed: int | None = None,
                conventions: dict[str, Any] | None = None,
                ephemeral: dict[str, Any] | None = None) -> dict[str, Any]:
    """Instantiate one schema-valid instance from a family template variant.

    ``ephemeral`` marks the instance as a runtime retry: it then carries its
    own question id and an explicit non-persistence record, so that it can
    never be confused with the frozen instance of the same family and variant.
    """
    family_id = template['family_id']
    variant_id = variant['variant_id']
    seed_key = variant.get('seed_key') or f'{family_id}-{variant_id}'
    if seed is None:
        seed = derive_seed(seed_key)
    prng = SplitMix64(seed)
    if conventions is None:
        raise VariantEngineError('E_VAR_NO_CONVENTIONS',
                                 'Konvenciju sala nav ielādēta; konstanti nevar atrisināt.')
    resolved = _resolve_inputs(conventions, variant)
    drawn = _draw_parameters(prng, variant)
    computed = _compute_derived(variant, {**resolved, **drawn})

    decimals: dict[str, int] = {}
    for param in variant_inputs(variant):
        if param['kind'] == 'int':
            decimals[param['param_id']] = int(param.get('display_decimals', param['decimals']))
        else:
            decimals[param['param_id']] = int(param.get('display_decimals', param.get('decimals', 0)))
    for derived in variant_derived(variant):
        decimals[derived['value_id']] = int(derived.get('display_decimals', derived.get('decimals', 6)))

    def dec_of(key: str) -> int:
        if key not in decimals:
            raise VariantEngineError('E_VAR_DECIMALS', f'No display precision declared for {key!r}.')
        return decimals[key]

    def literal(key: str) -> Num:
        if key not in computed:
            raise VariantEngineError('E_VAR_VALUE', f'Unknown value id {key!r}.')
        return num_literal(computed[key])

    def text_of(key: str) -> str:
        if key not in computed:
            raise VariantEngineError('E_VAR_VALUE', f'Unknown value id {key!r}.')
        return _format_latvian(computed[key], dec_of(key))

    payload_spec = variant.get('payload') or {}
    payload_class = payload_spec.get('class')
    payload: dict[str, Any] = {}

    # A numeric answer is graded against the value the learner is expected to
    # write: the computed value rounded to the declared significant figures.
    # The frozen N05 corpus stores its expected values the same way, and the
    # tolerance class is applied to that rounded value.
    answer_id = payload_spec.get('answer') if payload_class == 'numeric' else None
    answer_sig = int(payload_spec.get('sig_figs', 0)) if answer_id else 0
    answer_rounded = None
    answer_text = None
    render_decimals = dict(decimals)
    render_values = dict(computed)
    render_overrides: dict[str, str] = {}
    if answer_id and answer_sig:
        mode = payload_spec.get('round_mode', 'significant_figures')
        digits = int(payload_spec.get('round_digits', answer_sig))
        answer_rounded, answer_decimals = round_answer(computed[answer_id], mode, digits)
        render_decimals[answer_id] = answer_decimals
        render_values[answer_id] = answer_rounded
        # The written form is what the learner types and what the grader
        # counts. When the rubric carries a significant-figure criterion, the
        # written form has to carry the declared precision; a whole number
        # whose significant figures live in trailing zeros ("680") cannot,
        # so it is written in scientific notation ("6,80 × 10²"), which N17
        # parses and counts the same way.
        plain = _format_latvian(answer_rounded, answer_decimals)
        if (mode != 'decimal_places'
                and written_sig_figs(plain) != answer_sig
                and any(str(r.get('criterion_id', '')).endswith('_SIGFIG')
                        for r in (variant.get('rubric') or []))):
            answer_text = scientific_text(answer_rounded, answer_sig)
            render_overrides[answer_id] = answer_text

    if payload_class == 'numeric':
        payload = {
            'expected_value': literal(answer_id) if answer_rounded is None
            else num_literal(answer_rounded),
            'unit': payload_spec['unit'],
            'tolerance_class': payload_spec['tolerance_class'],
            # The payload records the significant figures of the written
            # answer form, which is what the grader compares against — the
            # same convention the frozen N05 corpus follows.
            'sig_figs': (written_sig_figs(answer_text) if answer_text
                         else (written_sig_figs(_format_latvian(answer_rounded,
                                                               render_decimals[answer_id]))
                               if answer_rounded is not None
                               else int(payload_spec['sig_figs']))),
            'display_lv': _render_text(payload_spec['display_lv'], render_values,
                                        render_decimals, render_overrides),
            'input_fields': [
                {'field_id': f['field_id'],
                 'label_lv': _render_text(f['label_lv'], render_values, render_decimals,
                                          render_overrides),
                 'kind': f.get('kind', 'number')}
                for f in payload_spec.get('input_fields') or []
            ],
        }
        if payload_spec.get('substeps'):
            payload['substeps'] = [
                {'step_id': s['step_id'], 'prompt_lv': _render_text(s['prompt_lv'], computed, decimals),
                 'expected_value': literal(s['answer'])}
                for s in payload_spec['substeps']
            ]
    elif payload_class == 'option_select':
        payload = {
            'options': [
                {'option_id': o['option_id'], 'text_lv': _render_text(o['text_lv'], computed, decimals)}
                for o in payload_spec['options']
            ],
            'correct_ids': list(payload_spec['correct_ids']),
            'distractors': [
                {'option_id': d['option_id'], 'rationale_lv': _render_text(d['rationale_lv'], computed, decimals)}
                for d in payload_spec.get('distractors') or []
            ],
            'requires_justification': bool(payload_spec.get('requires_justification', False)),
        }
        if payload_spec.get('justification_prompt_lv'):
            payload['justification_prompt_lv'] = _render_text(
                payload_spec['justification_prompt_lv'], computed, decimals)
    elif payload_class == 'ordering':
        payload = {
            'items': [
                {'item_id': i['item_id'], 'text_lv': _render_text(i['text_lv'], computed, decimals)}
                for i in payload_spec['items']
            ],
            'correct_order': list(payload_spec['correct_order']),
            'explanation_prompt_lv': _render_text(payload_spec['explanation_prompt_lv'], computed, decimals),
        }
        if payload_spec.get('partial_order_rules'):
            payload['partial_order_rules'] = payload_spec['partial_order_rules']
    elif payload_class == 'matching':
        payload = {
            'left_items': [
                {'id': i['id'], 'text_lv': _render_text(i['text_lv'], computed, decimals)}
                for i in payload_spec['left_items']
            ],
            'right_items': [
                {'id': i['id'], 'text_lv': _render_text(i['text_lv'], computed, decimals)}
                for i in payload_spec['right_items']
            ],
            'correct_pairs': [
                {'left_id': p['left_id'], 'right_id': p['right_id']} for p in payload_spec['correct_pairs']
            ],
        }
    elif payload_class == 'graph':
        points = []
        for point in payload_spec['points']:
            x = point['x']
            y = point['y']
            points.append({
                'x': literal(x) if isinstance(x, str) else Num(_plain_number(x), 0),
                'y': literal(y) if isinstance(y, str) else Num(_plain_number(y), 0),
            })
        readout = payload_spec['target_readout']
        payload = {
            'mode': payload_spec['mode'],
            'x_axis': {'label_lv': payload_spec['x_axis']['label_lv'], 'unit': payload_spec['x_axis']['unit']},
            'y_axis': {'label_lv': payload_spec['y_axis']['label_lv'], 'unit': payload_spec['y_axis']['unit']},
            'points': points,
            'target_readout': {
                'quantity': readout['quantity'],
                'expected_value': literal(readout['answer']),
                'unit': readout['unit'],
                'tolerance_class': readout['tolerance_class'],
            },
        }
    elif payload_class == 'method':
        steps = []
        for step in payload_spec['steps']:
            expected = step['expected']
            if isinstance(expected, str) and expected in computed:
                rendered: Any = text_of(expected)
            elif isinstance(expected, str):
                rendered = _render_text(expected, computed, decimals)
            else:
                rendered = expected
            steps.append({'step_id': step['step_id'],
                          'prompt_lv': _render_text(step['prompt_lv'], computed, decimals),
                          'expected': rendered})
        payload = {
            'steps': steps,
            'explanation_prompt_lv': _render_text(payload_spec['explanation_prompt_lv'], computed, decimals),
            'expected_summary_lv': _render_text(payload_spec['expected_summary_lv'], computed, decimals),
        }
        if payload_spec.get('species_list'):
            payload['species_list'] = list(payload_spec['species_list'])
        if payload_spec.get('medium'):
            payload['medium'] = payload_spec['medium']
    else:
        raise VariantEngineError('E_VAR_PAYLOAD_CLASS', f'Unknown payload class {payload_class!r}.')

    givens: dict[str, Any] = {}
    for key, value in (variant.get('givens_static') or {}).items():
        givens[key] = _render_text(value, computed, decimals) if isinstance(value, str) else value
    for key in payload_spec.get('givens_from') or []:
        if key not in computed:
            continue
        chosen = False
        for param in variant_inputs(variant):
            if param['param_id'] == key and param['kind'] == 'choice':
                givens[key] = param['choices'][computed[key]]
                chosen = True
                break
        if not chosen:
            givens[key] = literal(key)

    feedback = variant.get('feedback_lv') or {}
    feedback_lv = {
        'correct': _render_text(feedback.get('correct', 'Pareizi.'), computed, decimals),
        'incorrect': _render_text(feedback.get('incorrect', 'Pārbaudi aprēķinu.'), computed, decimals),
    }
    if feedback.get('hint'):
        feedback_lv['hint'] = _render_text(feedback['hint'], computed, decimals)

    rubric = [
        {
            'criterion_id': r['criterion_id'],
            'points': _number_value(r['points']),
            'grading': r.get('grading', 'auto'),
            'engine_binding': r.get('engine_binding', 'N17-numeric'),
            'depends_on': list(r.get('depends_on') or []),
            'carry_forward': bool(r.get('carry_forward', False)),
        }
        for r in variant.get('rubric') or []
    ]

    type_id = variant['type_id']
    if ephemeral is not None:
        attempt = int(ephemeral.get('attempt', 0))
        question_id = (f"COL1-{template['topic']}-{family_id[4:]}-{variant_id}"
                       f"-EPH-{attempt}")
    else:
        question_id = f"COL1-{template['topic']}-{family_id[4:]}-{variant_id}-01"
    instance = {
        'question_id': question_id,
        'schema_version': 1,
        'bank_version': BANK_VERSION,
        'family_id': family_id,
        'variant_id': variant_id,
        'seed': str(seed),
        'topic': template['topic'],
        'outcome_ids': list(template.get('outcome_ids') or []),
        'type_id': type_id,
        'type_ids': list(variant.get('type_ids') or [type_id]),
        'difficulty': variant.get('difficulty', 'application'),
        'time_minutes': _number_value(variant.get('time_minutes', 5)),
        'stem_lv': _render_text(variant['stem_lv'], computed, decimals),
        'feedback_lv': feedback_lv,
        'misconception_signatures': list(variant.get('misconception_signatures') or []),
        'source_refs': list(variant.get('source_refs') or []),
        'givens': givens,
        'payload_class': payload_class,
        'payload': payload,
        'rubric': rubric,
        'review': dict(variant.get('review') or {'content': 'pending', 'source': 'pending',
                                                  'calculation': 'pending', 'accessibility': 'pending'}),
        'extensions': {
            'extension_type': 'n20-variant-instance',
            'data': {
                'engine_id': ENGINE_ID,
                'engine_version': ENGINE_VERSION,
                'family_id': family_id,
                'variant_id': variant_id,
                'seed_key': seed_key,
                'seed_algorithm': SEED_ALGORITHM,
                'point_weight': _number_value(template.get('point_weight')),
                'spec_lv': variant.get('spec_lv'),
                'draws': [_draw_record(p, computed, text_of) for p in variant_inputs(variant)],
                'derived': [
                    {
                        'value_id': d['value_id'],
                        'op': d['op'],
                        'args': list(d['args']),
                        'value': text_of(d['value_id']),
                        'engine_path': d.get('engine_path'),
                        'role': d.get('role', 'intermediate'),
                    }
                    for d in variant_derived(variant)
                ],
                'recipe': variant.get('recipe') or {},
            },
        },
    }
    if ephemeral is not None:
        # The ephemeral instance is never persisted and never enters the frozen
        # bank. It carries its own identity so that no consumer can mistake it
        # for the frozen instance of the same family and variant.
        instance['extensions']['data']['ephemeral'] = {
            'attempt': int(ephemeral.get('attempt', 0)),
            'seed': str(seed),
            'persisted': False,
            'frozen_bank_member': False,
        }
    return instance


def instantiate_ephemeral(template: dict[str, Any], variant: dict[str, Any],
                           attempt: int = 0, frozen_seeds: Sequence[Any] = (),
                           conventions: dict[str, Any] | None = None) -> dict[str, Any]:
    """Instantiate a runtime retry that never touches the frozen bank.

    The seed is drawn outside the frozen seed set (the exclusion rule), the
    instance is produced by the same code path as a frozen instance and it is
    returned to the caller without being written anywhere.
    """
    family_id = template['family_id']
    variant_id = variant['variant_id']
    seed, attempt = ephemeral_seed(family_id, variant_id, attempt, frozen_seeds)
    instance = instantiate(template, variant, seed=seed,
                           conventions=conventions,
                           ephemeral={'attempt': attempt})
    instance['extensions']['data']['ephemeral']['excluded_frozen_seeds'] = True
    return instance


def _plain_number(value: Any) -> str:
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value != int(value):
            raise VariantEngineError('E_VAR_FLOAT',
                                     'Grafika koordināta nevar būt daļskaitlis; izmanto vērtības id.')
        return str(int(value))
    raise VariantEngineError('E_VAR_TYPE', f'Grafika koordināta tips nav atbalstīts: {type(value).__name__}')


def _number_value(value: Any) -> Any:
    """Keep a whole number a whole number (JSON has no int/float distinction
    for the reader, but the canonical writer's text does)."""
    if isinstance(value, bool):
        return value
    if isinstance(value, float) and value == int(value):
        return int(value)
    return value


def instantiate_all(templates: Sequence[dict[str, Any]],
                    conventions: dict[str, Any]) -> list[dict[str, Any]]:
    instances: list[dict[str, Any]] = []
    for family in templates:
        for variant in family.get('variants') or []:
            instances.append(instantiate(family, variant, conventions=conventions))
    return instances


def instance_digest(instance: dict[str, Any]) -> str:
    return sha256_bytes(canonical_bytes(instance))


# ------------------------------------------------------------------------ CLI

def _cmd_validate(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    templates = load_templates(repo_root / args.templates)
    report = validate_templates(templates, repo_root)
    report['template_digest'] = template_digest(templates)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'PASS' else 1


def _cmd_instantiate(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    templates = load_templates(repo_root / args.templates)
    conventions = json.loads((repo_root / 'data/conventions.json').read_text(encoding='utf-8'))
    for family in templates:
        if family['family_id'] != args.family:
            continue
        for variant in family['variants']:
            if variant['variant_id'] != args.variant:
                continue
            instance = instantiate(family, variant, conventions=conventions)
            sys.stdout.write(canonical_bytes(instance).decode('utf-8') + '\n')
            return 0
    print(f'Family/variant not found: {args.family}/{args.variant}', file=sys.stderr)
    return 1


def _cmd_emit(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    templates = load_templates(repo_root / args.templates)
    conventions = json.loads((repo_root / 'data/conventions.json').read_text(encoding='utf-8'))
    bank_dir = repo_root / args.bank
    bank_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for family in templates:
        instances = [instantiate(family, v, conventions=conventions) for v in family['variants']]
        path = bank_dir / f"{family['family_id']}.json"
        payload = {'questions': instances}
        path.write_bytes(canonical_bytes(payload) + b'\n')
        written.append(str(path.relative_to(repo_root)))
    print(json.dumps({'written': written, 'instances': sum(1 for _ in written) * 4},
                     ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='N20 variant engine (Python authoring twin).')
    parser.add_argument('--repo-root', default='.')
    sub = parser.add_subparsers(dest='command', required=True)

    p_validate = sub.add_parser('validate', help='Validate the family templates.')
    p_validate.add_argument('--templates', default='data/family_templates')
    p_validate.set_defaults(func=_cmd_validate)

    p_inst = sub.add_parser('instantiate', help='Instantiate one family variant to stdout.')
    p_inst.add_argument('--templates', default='data/family_templates')
    p_inst.add_argument('--family', required=True)
    p_inst.add_argument('--variant', required=True)
    p_inst.set_defaults(func=_cmd_instantiate)

    p_emit = sub.add_parser('emit', help='Emit the full bank into the source directory.')
    p_emit.add_argument('--templates', default='data/family_templates')
    p_emit.add_argument('--bank', default='data/bank')
    p_emit.set_defaults(func=_cmd_emit)

    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except VariantEngineError as error:
        print(f'{error}', file=sys.stderr)
        return 2
    except PrngError as error:
        print(f'{error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

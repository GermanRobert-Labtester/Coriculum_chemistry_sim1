/* N20 variant engine (JavaScript runtime twin).
 *
 * The runtime half of the practice-instance generator. It mirrors
 * tools/variant_engine.py byte for byte: identical family template plus
 * identical seed produce a byte-identical instance, which is what makes the
 * frozen bank auditable and the ephemeral retry path comparable with it.
 *
 * DESIGN NOTES
 *  - All arithmetic is fixed-point integer arithmetic on BigInt with a fixed
 *    scale. No IEEE-754 float ever reaches an emitted number, so the two
 *    languages cannot drift on a rounding boundary.
 *  - The seed is derived from the family/variant seed key with FNV-1a 64-bit
 *    over UTF-8; the draws come from the N05 SplitMix64 stream (src/prng.js).
 *  - The ephemeral retry path never persists: it returns an instance to the
 *    caller and keeps no store of it.
 *  - This module ships from src/ and is not inlined into the artifact; the
 *    runtime JavaScript budget in Section 1.3 has no headroom (N31 owns the
 *    inline / lazy-load / re-budget decision).
 */
(function (root) {
  'use strict';

  var ENGINE_ID = 'n20-variant-engine';
  var ENGINE_VERSION = '1.0.0';
  var TEMPLATE_ISLAND_ID = 'sim-family-templates';
  var BANK_ISLAND_ID = 'sim-bank';
  var BANK_VERSION = '1.0.0-n20';
  var BANK_STATUS = 'frozen-reviewed-bank';

  var SCALE = 9n;
  var SCALE_FACTOR = 10n ** SCALE;
  var SEED_ALGORITHM = 'fnv1a64-utf8-v1';
  var FNV_OFFSET = 0xCBF29CE484222325n;
  var FNV_PRIME = 0x100000001B3n;
  var MASK_64 = 0xFFFFFFFFFFFFFFFFn;

  var TYPE_IDS = [];
  for (var ti = 1; ti <= 18; ti += 1) { TYPE_IDS.push('Q' + (ti < 10 ? '0' : '') + ti); }
  var PAYLOAD_CLASSES = ['numeric', 'option_select', 'ordering', 'matching', 'graph', 'method'];
  var RECIPE_OPS = ['identity', 'add', 'sub', 'mul', 'div', 'mul_div', 'lin', 'pow_int', 'percent',
    'negate', 'log10_pow10', 'round_decimals'];

  var state = { templates: null, templateById: null, templateDigest: null, conventions: null };

  function VariantEngineError(code, message, details) {
    this.name = 'VariantEngineError';
    this.code = code;
    this.message = '[' + code + '] ' + message;
    this.details = details || {};
    if (Error.captureStackTrace) { Error.captureStackTrace(this, VariantEngineError); }
    else { this.stack = new Error(this.message).stack; }
  }
  VariantEngineError.prototype = Object.create(Error.prototype);
  VariantEngineError.prototype.constructor = VariantEngineError;

  function fail(code, message, details) { throw new VariantEngineError(code, message, details); }

  // ------------------------------------------------------------------ numbers

  function Num(text, value) { this.text = text; this.value = value; }

  function halfUpDiv(num, den) {
    if (den === 0n) { fail('E_VAR_DIV_ZERO', 'Receptes dalījums ar nulli.'); }
    var n = num; var d = den;
    if (d < 0n) { n = -n; d = -d; }
    var sign = n < 0n ? -1n : 1n;
    var mag = n < 0n ? -n : n;
    var q = (2n * mag + d) / (2n * d);
    return sign * q;
  }

  function fixedFromScaled(scaled, decimals) {
    if (decimals > Number(SCALE)) {
      fail('E_VAR_SCALE', 'Parametra decimāldašas (' + decimals + ') pārsniedz fiksēto punktu skalu (' + SCALE + ').');
    }
    return BigInt(scaled) * (10n ** BigInt(Number(SCALE) - Number(decimals)));
  }

  function fixedToDecimalText(value, decimals) {
    var neg = value < 0n;
    var mag = neg ? -value : value;
    var divisor = 10n ** BigInt(decimals);
    var whole = mag / divisor;
    var frac = mag % divisor;
    var text;
    if (decimals > 0) {
      var fracText = frac.toString();
      while (fracText.length < decimals) { fracText = '0' + fracText; }
      text = whole.toString() + '.' + fracText;
    } else {
      text = whole.toString();
    }
    return neg ? '-' + text : text;
  }

  /* Exact decimal text for a JSON number that is not an integer. Mirrors
   * tools/variant_engine.py:exact_number_text: shortest round-trip form,
   * exponent form and excessive precision refused. */
  function exactNumberText(value) {
    if (!Number.isFinite(value)) { fail('E_VAR_FLOAT', 'Nav pieņemama skaitļa vērtība.'); }
    if (Number.isInteger(value)) { return String(value); }
    var text = String(value);
    if (text.indexOf('e') >= 0 || text.indexOf('E') >= 0) {
      fail('E_VAR_FLOAT', 'Skaitlis ' + text + ' vajag vairāk nekā ' + String(SCALE) + ' decimāldašu.');
    }
    var dot = text.indexOf('.');
    if (dot >= 0 && text.length - dot - 1 > Number(SCALE)) {
      fail('E_VAR_FLOAT', 'Skaitlis ' + text + ' vajag vairāk nekā ' + String(SCALE) + ' decimāldašu.');
    }
    return text;
  }

  function numLiteral(value) {
    var text = fixedToDecimalText(value, Number(SCALE));
    if (text.indexOf('.') >= 0) {
      text = text.replace(/0+$/, '').replace(/\.$/, '');
      if (text === '' || text === '-') { text = '0'; }
      if (text === '-0') { text = '0'; }
    }
    /* A plain JSON number, not a wrapper object. The emitted instance has to
     * be readable by the N17 grading engine, which reads the expected value
     * with Number(), and it has to compare byte for byte with the frozen
     * bank, whose numbers are plain JSON numbers too. The canonical writer
     * prints the shortest round-trip decimal text, which is exactly the text
     * the Python twin writes for the same value; a value that JavaScript
     * cannot print without an exponent is refused rather than approximated. */
    return Number(text);
  }

  function digitCount(value) {
    if (value === 0n) { return 1; }
    return (value < 0n ? -value : value).toString().length;
  }

  /* Round a fixed-point integer to `sig` significant figures, half away from
   * zero. The rule belongs to the conventions; this integer implementation
   * keeps the two language twins byte-identical. The review gate proves it
   * agrees with the N17 engine on every numeric instance. */
  function roundToSigFigs(value, sig) {
    if (sig < 1) { fail('E_VAR_SCALE', 'Zīmīgo ciparu skaitam jābūt vismaz 1.'); }
    if (value === 0n) { return 0n; }
    var digits = digitCount(value);
    if (digits <= sig) { return value; }
    var quantum = 10n ** BigInt(digits - sig);
    var magnitude = value < 0n ? -value : value;
    var quotient = magnitude / quantum;
    var remainder = magnitude % quantum;
    if (remainder * 2n >= quantum) { quotient += 1n; }
    var result = quotient * quantum;
    return value < 0n ? -result : result;
  }

  /* Decimal places that make the written form carry `sig` significant figures. */
  function sigFigDecimals(value, sig) {
    if (value === 0n) { return Math.max(0, sig - 1); }
    var integerDigits = Math.max(0, digitCount(value) - Number(SCALE));
    return Math.max(0, sig - integerDigits);
  }

  // ------------------------------------------------------------- canonical IO

  function writeCanonical(value, out) {
    if (value === null || value === undefined) { out.push('null'); return; }
    if (value instanceof Num) { out.push(value.text); return; }
    if (value === true) { out.push('true'); return; }
    if (value === false) { out.push('false'); return; }
    if (typeof value === 'bigint') { out.push(value.toString()); return; }
    if (typeof value === 'number') {
      if (!Number.isFinite(value)) { fail('E_VAR_FLOAT', 'Nav pieņemama skaitļa vērtība.'); }
      if (Number.isInteger(value)) { out.push(String(value)); return; }
      out.push(exactNumberText(value));
      return;
    }
    if (typeof value === 'string') { out.push(JSON.stringify(value)); return; }
    if (Array.isArray(value)) {
      out.push('[');
      for (var i = 0; i < value.length; i += 1) {
        if (i) { out.push(','); }
        writeCanonical(value[i], out);
      }
      out.push(']');
      return;
    }
    if (typeof value === 'object') {
      var keys = Object.keys(value).sort();
      out.push('{');
      for (var k = 0; k < keys.length; k += 1) {
        if (k) { out.push(','); }
        out.push(JSON.stringify(keys[k]));
        out.push(':');
        writeCanonical(value[keys[k]], out);
      }
      out.push('}');
      return;
    }
    fail('E_VAR_TYPE', 'Nepazīstams tips emitējamai vērtībai: ' + typeof value);
  }

  function canonicalText(value) {
    var out = [];
    writeCanonical(value, out);
    return out.join('');
  }

  function canonicalBytes(value) {
    return utf8Bytes(canonicalText(value));
  }

  function utf8Bytes(text) {
    var out = [];
    for (var i = 0; i < text.length; i += 1) {
      var code = text.charCodeAt(i);
      if (code < 0x80) { out.push(code); }
      else if (code < 0x800) { out.push(0xC0 | (code >> 6), 0x80 | (code & 63)); }
      else if (code >= 0xD800 && code <= 0xDBFF && i + 1 < text.length) {
        var next = text.charCodeAt(i + 1);
        code = 0x10000 + (((code & 0x3FF) << 10) | (next & 0x3FF));
        i += 1;
        out.push(0xF0 | (code >> 18), 0x80 | ((code >> 12) & 63), 0x80 | ((code >> 6) & 63), 0x80 | (code & 63));
      } else {
        out.push(0xE0 | (code >> 12), 0x80 | ((code >> 6) & 63), 0x80 | (code & 63));
      }
    }
    return new Uint8Array(out);
  }

  function sha256Hex(value) {
    if (root.SimFigures && typeof root.SimFigures.sha256Utf8 === 'function') {
      return root.SimFigures.sha256Utf8(canonicalText(value));
    }
    fail('E_VAR_SHA', 'SHA-256 palīgs nav pieejams (ielādē SimFigures).');
  }

  // ----------------------------------------------------------- conventions refs

  /* Resolve a conventions reference to its numeric text. Mirrors
   * tools/variant_engine.py:resolve_convention exactly. */
  function resolveConvention(conventions, ref) {
    var kind = String(ref).split(':')[0];
    var rest = String(ref).slice(kind.length + 1);
    if (kind === 'molar_mass') {
      var compounds = (conventions.compound_molar_masses || {}).compounds || [];
      for (var i = 0; i < compounds.length; i += 1) {
        if (compounds[i].formula === rest) {
          var wv = compounds[i].working_value;
          return String(wv !== undefined && wv !== null ? wv : compounds[i].value);
        }
      }
    } else if (kind === 'atomic_mass') {
      var elements = (conventions.atomic_masses || {}).elements || [];
      for (var e = 0; e < elements.length; e += 1) {
        if (elements[e].symbol === rest) { return String(elements[e].value); }
      }
    } else if (kind === 'constant') {
      var constants = (conventions.constants || {}).values || [];
      for (var c = 0; c < constants.length; c += 1) {
        if (constants[c].id === rest) { return String(constants[c].value); }
      }
    } else if (kind === 'potential') {
      var potentials = (conventions.potentials || {}).reference_values || [];
      for (var p = 0; p < potentials.length; p += 1) {
        if (potentials[p].id === rest) { return String(potentials[p].value); }
      }
    } else if (kind === 'nernst_slope') {
      return String(conventions.potentials.nernst.slope_V);
    } else if (kind === 'conversion') {
      var parts = rest.split(':');
      var which = parts.length > 1 ? parts[1] : 'num';
      var conversions = (conventions.unit_system || {}).conversions || [];
      for (var v = 0; v < conversions.length; v += 1) {
        if (conversions[v].id === parts[0]) {
          var factor = conversions[v].factor || {};
          if (which === 'num' || which === 'den') { return String(factor[which]); }
        }
      }
    }
    fail('E_VAR_CONVENTION_REF', 'Konvenciju atsauce neatris: ' + ref);
  }

  /* Decimal string -> fixed-point integer. Mirrors the Python Decimal path
   * (exact, truncated toward zero) without any float arithmetic. */
  function decimalToFixed(text, decimals) {
    var raw = String(text).trim();
    if (raw.indexOf('e') >= 0 || raw.indexOf('E') >= 0) {
      fail('E_VAR_CONVENTION_REF', 'Eksponenciālā konvenciju vērtība nav atbalstīta: ' + raw);
    }
    var negative = raw.charAt(0) === '-';
    if (negative) { raw = raw.slice(1); }
    var dot = raw.indexOf('.');
    var whole = dot >= 0 ? raw.slice(0, dot) : raw;
    var frac = dot >= 0 ? raw.slice(dot + 1) : '';
    if (!/^[0-9]*$/.test(whole) || !/^[0-9]*$/.test(frac)) {
      fail('E_VAR_CONVENTION_REF', 'Konvenciju vērtība nav decimālda skaitlis: ' + text);
    }
    if (frac.length > decimals) {
      fail('E_VAR_CONVENTION_REF',
        'Konvenciju vērtībai ' + text + ' ir vairāk decimāldašu, nekā deklarēts (' + decimals + ').');
    }
    var padded = frac + '0'.repeat(Math.max(0, decimals - frac.length));
    var scaled = BigInt((whole || '0') + padded);
    return negative ? -scaled : scaled;
  }

  // ----------------------------------------------------------------- seed rules

  function deriveSeed(seedKey) {
    if (typeof seedKey !== 'string' || seedKey.trim() === '') {
      fail('E_VAR_SEED_KEY', 'Seed key must be a non-empty string.');
    }
    var bytes = utf8Bytes(seedKey);
    var digest = FNV_OFFSET;
    for (var i = 0; i < bytes.length; i += 1) {
      digest = (digest ^ BigInt(bytes[i])) & MASK_64;
      digest = (digest * FNV_PRIME) & MASK_64;
    }
    if (digest === 0n) { digest = 1n; }
    return digest;
  }

  function ephemeralSeed(familyId, variantId, attempt, frozenSeeds) {
    var frozen = Object.create(null);
    var list = frozenSeeds || [];
    for (var i = 0; i < list.length; i += 1) { frozen[String(list[i])] = true; }
    var counter = Number(attempt || 0);
    var guard = 0;
    while (guard < 100000) {
      var seed = deriveSeed(familyId + '-' + variantId + '-EPH-' + counter);
      if (!frozen[seed.toString()]) { return { seed: seed, attempt: counter }; }
      counter += 1;
      guard += 1;
    }
    fail('E_VAR_SEED_EXHAUSTED', 'Neatrasta brīva pagaidu sēkla.');
  }

  // --------------------------------------------------------------- recipe eval

  function evalRecipe(op, args) {
    if (op === 'identity') { return args[0]; }
    if (op === 'add') { return args[0] + args[1]; }
    if (op === 'sub') { return args[0] - args[1]; }
    if (op === 'mul') { return halfUpDiv(args[0] * args[1], SCALE_FACTOR); }
    if (op === 'div') { return halfUpDiv(args[0] * SCALE_FACTOR, args[1]); }
    if (op === 'mul_div') { return halfUpDiv(args[0] * args[1], args[2]); }
    if (op === 'lin') { return halfUpDiv(args[0] * args[1], SCALE_FACTOR) + args[2]; }
    if (op === 'pow_int') {
      var exponent = args[1];
      if (exponent < 0n) { fail('E_VAR_RECIPE', 'pow_int requires a non-negative exponent.'); }
      var result = SCALE_FACTOR;
      for (var i = 0; i < Number(exponent); i += 1) { result = halfUpDiv(result * args[0], SCALE_FACTOR); }
      return result;
    }
    if (op === 'percent') { return halfUpDiv(args[0] * 100n * SCALE_FACTOR, args[1]); }
    if (op === 'negate') { return -args[0]; }
    if (op === 'log10_pow10') { return log10Pow10(args[0]); }
    if (op === 'round_decimals') {
      var rd = args[1] / SCALE_FACTOR;
      if (args[1] % SCALE_FACTOR !== 0n) {
        fail('E_VAR_RECIPE', 'round_decimals requires a whole decimal count.');
      }
      return roundToDecimals(args[0], Number(rd));
    }
    fail('E_VAR_RECIPE', 'Nezināma receptes operācija: ' + String(op));
  }

  /* Round a fixed-point integer to `decimals` decimal places, half away from
   * zero. Reading items are reported to a fixed precision rather than to a
   * number of significant figures. */
  function roundToDecimals(value, decimals) {
    if (decimals < 0 || decimals > Number(SCALE)) {
      fail('E_VAR_SCALE', 'Decimāldašu skaits ārpus 0..' + String(SCALE) + '.');
    }
    var quantum = 10n ** (SCALE - BigInt(decimals));
    var magnitude = value < 0n ? -value : value;
    var quotient = magnitude / quantum;
    var remainder = magnitude % quantum;
    if (remainder * 2n >= quantum) { quotient += 1n; }
    var result = quotient * quantum;
    return value < 0n ? -result : result;
  }

  /* Round a computed answer and report the decimals its written form needs. */
  function roundAnswer(value, mode, digits) {
    if (mode === 'decimal_places') {
      var roundedDp = roundToDecimals(value, digits);
      return { value: roundedDp, decimals: digits };
    }
    var roundedSf = roundToSigFigs(value, digits);
    return { value: roundedSf, decimals: sigFigDecimals(roundedSf, digits) };
  }

  /* Exact decimal logarithm of an exact power of ten. Counting trailing
   * decimal zeros keeps the operation integer-only, so the two language
   * twins cannot drift; a value that is not a power of ten is a hard
   * failure, never an approximation. */
  function log10Pow10(value) {
    if (value <= 0n) { fail('E_VAR_RECIPE', 'log10_pow10 requires a positive value.'); }
    var magnitude = value;
    var zeros = 0;
    while (magnitude % 10n === 0n) {
      magnitude = magnitude / 10n;
      zeros += 1;
    }
    if (magnitude !== 1n) {
      fail('E_VAR_RECIPE', 'log10_pow10 requires an exact power of ten.');
    }
    var exponent = zeros - Number(SCALE);
    if (exponent < 0) { fail('E_VAR_RECIPE', 'log10_pow10 requires a value >= 1.'); }
    return BigInt(exponent) * SCALE_FACTOR;
  }

  // ------------------------------------------------------------------ templates

  function load(templates, conventions) {
    if (!templates || !Array.isArray(templates.families)) {
      fail('E_VAR_TEMPLATE_SHAPE', 'Template kopums nav piegādāts vai tam nav families.');
    }
    if (templates.island_id && templates.island_id !== TEMPLATE_ISLAND_ID) {
      fail('E_VAR_TEMPLATE_ISLAND', 'Template kopuma island_id nav ' + TEMPLATE_ISLAND_ID + '.');
    }
    state.templates = templates;
    state.conventions = conventions || null;
    state.templateById = Object.create(null);
    for (var i = 0; i < templates.families.length; i += 1) {
      state.templateById[templates.families[i].family_id] = templates.families[i];
    }
    state.templateDigest = digestOf(templates.families);
    return templates;
  }

  function requireLoaded() {
    if (!state.templates) { fail('E_VAR_NOT_LOADED', 'Variantu motoram nav ielādētu ģimeņu veidotu.'); }
  }

  function digestOf(value) { return sha256Hex(value); }

  /* Ordered, non-drawn inputs of a variant: the declared parameters plus any
   * constant/fixed specification declared among the derived values. Mirrors
   * tools/variant_engine.py:variant_inputs. */
  function variantInputs(variant) {
    var inputs = [];
    var seen = Object.create(null);
    var params = variant.parameters || [];
    for (var i = 0; i < params.length; i += 1) {
      var pid = params[i].param_id;
      if (seen[pid]) { fail('E_VAR_DUPLICATE_INPUT', 'Dubultā ievades deklarācija: ' + pid); }
      seen[pid] = true;
      inputs.push(params[i]);
    }
    var derived = variant.derived || [];
    for (var d = 0; d < derived.length; d += 1) {
      var kind = derived[d].kind;
      if (kind !== 'constant' && kind !== 'fixed') { continue; }
      var did = derived[d].param_id;
      if (seen[did]) { fail('E_VAR_DUPLICATE_INPUT', 'Dubultā ievades deklarācija: ' + did); }
      seen[did] = true;
      inputs.push(derived[d]);
    }
    return inputs;
  }

  function variantDerived(variant) {
    return (variant.derived || []).filter(function (d) {
      return d.kind !== 'constant' && d.kind !== 'fixed';
    });
  }

  /* Resolve the non-drawn inputs: conventions constants by reference and
   * authored fixed factors. */
  function resolveInputs(conventions, variant) {
    if (!conventions) {
      fail('E_VAR_NO_CONVENTIONS', 'Konvenciju sala nav ielādēta; konstanti nevar atrisināt.');
    }
    var resolved = Object.create(null);
    var inputs = variantInputs(variant);
    for (var i = 0; i < inputs.length; i += 1) {
      var spec = inputs[i];
      var decimals = spec.decimals === undefined ? 0 : Number(spec.decimals);
      if (spec.kind === 'constant') {
        var raw = resolveConvention(conventions, spec.conventions_ref);
        resolved[spec.param_id] = fixedFromScaled(decimalToFixed(raw, decimals), decimals);
      } else if (spec.kind === 'fixed') {
        resolved[spec.param_id] = fixedFromScaled(Number(spec.value), decimals);
      }
    }
    return resolved;
  }

  // -------------------------------------------------------------- instantiation

  function drawParameters(prng, variant) {
    var drawn = Object.create(null);
    var inputs = variantInputs(variant);
    for (var i = 0; i < inputs.length; i += 1) {
      var param = inputs[i];
      if (param.kind === 'choice') {
        drawn[param.param_id] = BigInt(prng.nextInt(param.choices.length));
        continue;
      }
      if (param.kind !== 'int') { continue; }
      var span = (param.max - param.min) / param.step;
      var index = prng.nextInt(Number(span) + 1);
      drawn[param.param_id] = fixedFromScaled(param.min + index * param.step, param.decimals);
    }
    return drawn;
  }

  function computeDerived(variant, values) {
    var computed = Object.create(null);
    var keys = Object.keys(values);
    for (var k = 0; k < keys.length; k += 1) { computed[keys[k]] = values[keys[k]]; }
    var derived = variantDerived(variant);
    for (var i = 0; i < derived.length; i += 1) {
      var spec = derived[i];
      var args = [];
      for (var a = 0; a < spec.args.length; a += 1) {
        if (!(spec.args[a] in computed)) { fail('E_VAR_VALUE', 'Nezināma vērtība: ' + spec.args[a]); }
        args.push(computed[spec.args[a]]);
      }
      computed[spec.value_id] = evalRecipe(spec.op, args);
    }
    return computed;
  }

  /* Keep a whole number a whole number; the canonical writer's text must not
   * depend on whether a value arrived as 3 or 3.0. */
  function numberValue(value) {
    if (typeof value !== 'number' || !Number.isFinite(value)) { return value; }
    return Number.isInteger(value) ? value : value;
  }

  function cloneValue(value) {
    if (Array.isArray(value)) { return value.map(cloneValue); }
    if (value && typeof value === 'object') {
      var out = {};
      var keys = Object.keys(value);
      for (var i = 0; i < keys.length; i += 1) { out[keys[i]] = cloneValue(value[keys[i]]); }
      return out;
    }
    return value;
  }

  function mergeValues(resolved, drawn) {    var merged = Object.create(null);
    var resolvedKeys = Object.keys(resolved);
    for (var i = 0; i < resolvedKeys.length; i += 1) { merged[resolvedKeys[i]] = resolved[resolvedKeys[i]]; }
    var drawnKeys = Object.keys(drawn);
    for (var d = 0; d < drawnKeys.length; d += 1) { merged[drawnKeys[d]] = drawn[drawnKeys[d]]; }
    return merged;
  }

  /* Render a fixed-point integer with the requested display precision. The
   * stored value is always in units of 10^-SCALE, so the display precision
   * rounds (half away from zero) first. Mirrors
   * tools/variant_engine.py:_format_latvian. */
  function formatLatvian(value, decimals) {
    if (decimals < 0 || decimals > Number(SCALE)) {
      fail('E_VAR_SCALE', 'Attēlotā decimāldašu skaita diapazons: 0..' + String(SCALE) + '.');
    }
    var neg = value < 0n;
    var mag = neg ? -value : value;
    var factor = 10n ** (SCALE - BigInt(decimals));
    var quotient = mag / factor;
    var remainder = mag % factor;
    if (remainder * 2n >= factor) { quotient += 1n; }
    var divisor = 10n ** BigInt(decimals);
    var whole = quotient / divisor;
    var frac = quotient % divisor;
    var text;
    if (decimals > 0) {
      var fracText = frac.toString();
      while (fracText.length < decimals) { fracText = '0' + fracText; }
      text = whole.toString() + '.' + fracText;
    } else {
      text = whole.toString();
    }
    return (neg ? '-' : '') + text.replace('.', ',');
  }

  function renderText(text, values, decimals, overrides) {
    var out = String(text);
    var keys = Object.keys(decimals);
    for (var i = 0; i < keys.length; i += 1) {
      var token = '{' + keys[i] + '}';
      if (out.indexOf(token) >= 0) {
        var replacement = (overrides && Object.prototype.hasOwnProperty.call(overrides, keys[i]))
          ? overrides[keys[i]]
          : formatLatvian(values[keys[i]], decimals[keys[i]]);
        out = out.split(token).join(replacement);
      }
    }
    return out;
  }

  /* Significant figures of a *written* number, by the N17 rule: with a
   * decimal point every digit counts, without one the trailing zeros are
   * ambiguous and do not count. The answer's written form is what a learner
   * types and what the grader counts, so the engine has to know the count of
   * the form it emits. */
  function writtenSigFigs(text) {
    var raw = String(text).trim();
    var scientific = /^([+-]?[0-9]+(?:[.,][0-9]*)?)\s*(?:[×x*]\s*10)/.exec(raw);
    var mantissa = scientific ? scientific[1] : raw.split(' ')[0];
    mantissa = mantissa.replace(/,/g, '.');
    if (mantissa.indexOf('.') >= 0) {
      var digits = mantissa.replace('.', '').replace(/^0+/, '');
      return digits.length ? digits.length : 1;
    }
    var bare = mantissa.replace(/^0+/, '').replace(/0+$/, '');
    return bare.length ? bare.length : 1;
  }

  var SUPERSCRIPT = { '0': '\u2070', '1': '\u00B9', '2': '\u00B2', '3': '\u00B3', '4': '\u2074',
    '5': '\u2075', '6': '\u2076', '7': '\u2077', '8': '\u2078', '9': '\u2079', '-': '\u207B', '+': '\u207A' };

  /* The answer in scientific notation, e.g. 680 at 3 significant figures.
   * A whole number whose significant figures live in trailing zeros ("680")
   * cannot carry them in plain notation: N17 counts "680" as two significant
   * figures. "6,80 x 10^2" carries three, and N17 parses it. */
  function scientificText(value, sig) {
    if (value === 0n) { fail('E_VAR_ZERO', 'Nulle nevar b\u0101t zin\u0101tniski rakst\u012bts.'); }
    var negative = value < 0n;
    var magnitude = negative ? -value : value;
    var exponent = digitCount(magnitude) - 1 - Number(SCALE);
    var mantissa = exponent >= 0
      ? magnitude / (10n ** BigInt(exponent))
      : magnitude * (10n ** BigInt(-exponent));
    var decimals = Math.max(0, sig - 1);
    var text = formatLatvian(mantissa, decimals);
    var exponentText = String(exponent).split('').map(function (ch) {
      return Object.prototype.hasOwnProperty.call(SUPERSCRIPT, ch) ? SUPERSCRIPT[ch] : ch;
    }).join('');
    return (negative ? '-' : '') + text + ' \u00D7 10' + exponentText;
  }

  function hasSigFigCriterion(variant) {
    var rubric = variant.rubric || [];
    for (var i = 0; i < rubric.length; i += 1) {
      if (String(rubric[i].criterion_id || '').slice(-7) === '_SIGFIG') { return true; }
    }
    return false;
  }

  function instantiate(familyId, variantId, seed, options) {
    requireLoaded();
    var family = state.templateById[familyId];
    if (!family) { fail('E_VAR_FAMILY', 'Ģimene nav atrasta: ' + familyId); }
    var variant = null;
    for (var i = 0; i < (family.variants || []).length; i += 1) {
      if (family.variants[i].variant_id === variantId) { variant = family.variants[i]; }
    }
    if (!variant) { fail('E_VAR_VARIANT', 'Variants nav atrasts: ' + familyId + '/' + variantId); }

    var seedKey = variant.seed_key || (familyId + '-' + variantId);
    var actualSeed = (seed === undefined || seed === null) ? deriveSeed(seedKey) : BigInt(seed);
    if (!root.SimPRNG || typeof root.SimPRNG.createStream !== 'function') {
      fail('E_VAR_PRNG', 'N05 PRNG (SimPRNG) nav pieejams.');
    }
    var prng = root.SimPRNG.createStream(actualSeed);
    var resolved = resolveInputs(state.conventions, variant);
    var drawn = drawParameters(prng, variant);
    var computed = computeDerived(variant, mergeValues(resolved, drawn));

    var decimals = Object.create(null);
    var inputs = variantInputs(variant);
    for (var p = 0; p < inputs.length; p += 1) {
      var disp = inputs[p].display_decimals !== undefined
        ? inputs[p].display_decimals
        : (inputs[p].decimals !== undefined ? inputs[p].decimals : 0);
      decimals[inputs[p].param_id] = Number(disp);
    }
    var derivedSpecs = variantDerived(variant);
    for (var d = 0; d < derivedSpecs.length; d += 1) {
      var ds = derivedSpecs[d];
      decimals[ds.value_id] = ds.display_decimals !== undefined
        ? ds.display_decimals : (ds.decimals !== undefined ? ds.decimals : 6);
    }

    function literal(key) {
      if (!(key in computed)) { fail('E_VAR_VALUE', 'Nezināma vērtība: ' + key); }
      return numLiteral(computed[key]);
    }
    function textOf(key) {
      if (!(key in computed)) { fail('E_VAR_VALUE', 'Nezināma vērtība: ' + key); }
      return formatLatvian(computed[key], decimals[key]);
    }

    var spec = variant.payload || {};
    var payloadClass = spec.class;
    var payload = {};

    /* A numeric answer is graded against the value the learner is expected to
     * write: the computed value rounded to the declared significant figures,
     * exactly as the frozen N05 corpus stores its expected values. */
    var answerId = payloadClass === 'numeric' ? spec.answer : null;
    var answerSig = answerId && spec.sig_figs ? Number(spec.sig_figs) : 0;
    var answerRounded = null;
    var renderDecimals = Object.create(null);
    var renderKeys = Object.keys(decimals);
    for (var rk = 0; rk < renderKeys.length; rk += 1) { renderDecimals[renderKeys[rk]] = decimals[renderKeys[rk]]; }
    var renderValues = Object.create(null);
    var computedKeys = Object.keys(computed);
    for (var ck = 0; ck < computedKeys.length; ck += 1) { renderValues[computedKeys[ck]] = computed[computedKeys[ck]]; }
    var answerText = null;
    var renderOverrides = Object.create(null);
    if (answerId && answerSig) {
      var mode = spec.round_mode || 'significant_figures';
      var digits = spec.round_digits === undefined ? answerSig : Number(spec.round_digits);
      var rounded = roundAnswer(computed[answerId], mode, digits);
      answerRounded = rounded.value;
      renderDecimals[answerId] = rounded.decimals;
      renderValues[answerId] = answerRounded;
      /* The written form is what the learner types and what the grader
       * counts. When the rubric carries a significant-figure criterion, the
       * written form has to carry the declared precision; a whole number
       * whose significant figures live in trailing zeros ("680") cannot, so
       * it is written in scientific notation ("6,80 x 10^2"), which N17
       * parses and counts the same way. */
      var plain = formatLatvian(answerRounded, rounded.decimals);
      if (mode !== 'decimal_places' && writtenSigFigs(plain) !== answerSig && hasSigFigCriterion(variant)) {
        answerText = scientificText(answerRounded, answerSig);
        renderOverrides[answerId] = answerText;
      }
    }

    if (payloadClass === 'numeric') {
      payload = {
        expected_value: answerRounded === null ? literal(answerId) : numLiteral(answerRounded),
        unit: spec.unit,
        tolerance_class: spec.tolerance_class,
        /* The payload records the significant figures of the written answer
         * form, which is what the grader compares against — the same
         * convention the frozen N05 corpus follows. */
        sig_figs: answerText ? writtenSigFigs(answerText)
          : (answerRounded === null ? Number(spec.sig_figs)
            : writtenSigFigs(formatLatvian(answerRounded, renderDecimals[answerId]))),
        display_lv: renderText(spec.display_lv, renderValues, renderDecimals, renderOverrides),
        input_fields: (spec.input_fields || []).map(function (f) {
          return { field_id: f.field_id, label_lv: renderText(f.label_lv, renderValues, renderDecimals, renderOverrides), kind: f.kind || 'number' };
        })
      };
      if (spec.substeps) {
        payload.substeps = spec.substeps.map(function (s) {
          return { step_id: s.step_id, prompt_lv: renderText(s.prompt_lv, computed, decimals), expected_value: literal(s.answer) };
        });
      }
    } else if (payloadClass === 'option_select') {
      payload = {
        options: (spec.options || []).map(function (o) {
          return { option_id: o.option_id, text_lv: renderText(o.text_lv, computed, decimals) };
        }),
        correct_ids: (spec.correct_ids || []).slice(),
        distractors: (spec.distractors || []).map(function (d) {
          return { option_id: d.option_id, rationale_lv: renderText(d.rationale_lv, computed, decimals) };
        }),
        requires_justification: Boolean(spec.requires_justification)
      };
      if (spec.justification_prompt_lv) {
        payload.justification_prompt_lv = renderText(spec.justification_prompt_lv, computed, decimals);
      }
    } else if (payloadClass === 'ordering') {
      payload = {
        items: (spec.items || []).map(function (i) {
          return { item_id: i.item_id, text_lv: renderText(i.text_lv, computed, decimals) };
        }),
        correct_order: (spec.correct_order || []).slice(),
        explanation_prompt_lv: renderText(spec.explanation_prompt_lv, computed, decimals)
      };
      if (spec.partial_order_rules) { payload.partial_order_rules = spec.partial_order_rules; }
    } else if (payloadClass === 'matching') {
      payload = {
        left_items: (spec.left_items || []).map(function (i) {
          return { id: i.id, text_lv: renderText(i.text_lv, computed, decimals) };
        }),
        right_items: (spec.right_items || []).map(function (i) {
          return { id: i.id, text_lv: renderText(i.text_lv, computed, decimals) };
        }),
        correct_pairs: (spec.correct_pairs || []).map(function (p) {
          return { left_id: p.left_id, right_id: p.right_id };
        })
      };
    } else if (payloadClass === 'graph') {
      var points = (spec.points || []).map(function (point) {
        return {
          x: typeof point.x === 'string' ? literal(point.x) : new Num(String(point.x), 0n),
          y: typeof point.y === 'string' ? literal(point.y) : new Num(String(point.y), 0n)
        };
      });
      var readout = spec.target_readout;
      payload = {
        mode: spec.mode,
        x_axis: { label_lv: spec.x_axis.label_lv, unit: spec.x_axis.unit },
        y_axis: { label_lv: spec.y_axis.label_lv, unit: spec.y_axis.unit },
        points: points,
        target_readout: {
          quantity: readout.quantity,
          expected_value: literal(readout.answer),
          unit: readout.unit,
          tolerance_class: readout.tolerance_class
        }
      };
    } else if (payloadClass === 'method') {
      var steps = (spec.steps || []).map(function (step) {
        var expected = step.expected;
        var rendered;
        if (typeof expected === 'string' && expected in computed) { rendered = textOf(expected); }
        else if (typeof expected === 'string') { rendered = renderText(expected, computed, decimals); }
        else { rendered = expected; }
        return { step_id: step.step_id, prompt_lv: renderText(step.prompt_lv, computed, decimals), expected: rendered };
      });
      payload = {
        steps: steps,
        explanation_prompt_lv: renderText(spec.explanation_prompt_lv, computed, decimals),
        expected_summary_lv: renderText(spec.expected_summary_lv, computed, decimals)
      };
      if (spec.species_list) { payload.species_list = spec.species_list.slice(); }
      if (spec.medium) { payload.medium = spec.medium; }
    } else {
      fail('E_VAR_PAYLOAD_CLASS', 'Nezināms payload klase: ' + String(payloadClass));
    }

    var givens = Object.create(null);
    var staticGivens = variant.givens_static || {};
    var staticKeys = Object.keys(staticGivens);
    for (var g = 0; g < staticKeys.length; g += 1) {
      var sv = staticGivens[staticKeys[g]];
      givens[staticKeys[g]] = (typeof sv === 'string') ? renderText(sv, computed, decimals) : sv;
    }
    var givenFrom = spec.givens_from || [];
    for (var gi = 0; gi < givenFrom.length; gi += 1) {
      var key = givenFrom[gi];
      if (!(key in computed)) { continue; }
      var isChoice = false;
      for (var cp = 0; cp < inputs.length; cp += 1) {
        if (inputs[cp].param_id === key && inputs[cp].kind === 'choice') {
          givens[key] = inputs[cp].choices[Number(computed[key])];
          isChoice = true;
          break;
        }
      }
      if (!isChoice) { givens[key] = literal(key); }
    }

    var feedback = variant.feedback_lv || {};
    var feedbackLv = {
      correct: renderText(feedback.correct || 'Pareizi.', computed, decimals),
      incorrect: renderText(feedback.incorrect || 'Pārbaudi aprēķinu.', computed, decimals)
    };
    if (feedback.hint) { feedbackLv.hint = renderText(feedback.hint, computed, decimals); }

    var rubric = (variant.rubric || []).map(function (r) {
      return {
        criterion_id: r.criterion_id,
        points: numberValue(r.points),
        grading: r.grading || 'auto',
        engine_binding: r.engine_binding || 'N17-numeric',
        depends_on: (r.depends_on || []).slice(),
        carry_forward: Boolean(r.carry_forward)
      };
    });

    var typeId = variant.type_id;
    var ephemeral = options && options.ephemeral ? options.ephemeral : null;
    var questionId = ephemeral
      ? 'COL1-' + family.topic + '-' + familyId.slice(4) + '-' + variantId +
        '-EPH-' + String(Number(ephemeral.attempt || 0))
      : 'COL1-' + family.topic + '-' + familyId.slice(4) + '-' + variantId + '-01';
    var instance = {
      question_id: questionId,
      schema_version: 1,
      bank_version: BANK_VERSION,
      family_id: familyId,
      variant_id: variantId,
      seed: actualSeed.toString(),
      topic: family.topic,
      outcome_ids: (family.outcome_ids || []).slice(),
      type_id: typeId,
      type_ids: (variant.type_ids || [typeId]).slice(),
      difficulty: variant.difficulty || 'application',
      time_minutes: numberValue(variant.time_minutes === undefined ? 5 : variant.time_minutes),
      stem_lv: renderText(variant.stem_lv, computed, decimals),
      feedback_lv: feedbackLv,
      misconception_signatures: (variant.misconception_signatures || []).slice(),
      source_refs: (variant.source_refs || []).map(cloneValue),
      givens: givens,
      payload_class: payloadClass,
      payload: payload,
      rubric: rubric,
      review: variant.review || { content: 'pending', source: 'pending', calculation: 'pending', accessibility: 'pending' },
      extensions: {
        extension_type: 'n20-variant-instance',
        data: {
          engine_id: ENGINE_ID,
          engine_version: ENGINE_VERSION,
          family_id: familyId,
          variant_id: variantId,
          seed_key: seedKey,
          seed_algorithm: SEED_ALGORITHM,
          point_weight: numberValue(family.point_weight),
          spec_lv: variant.spec_lv,
          draws: inputs.map(function (p) {
            var value;
            if (p.kind === 'choice') { value = p.choices[Number(computed[p.param_id])]; }
            else { value = textOf(p.param_id); }
            var record = {
              param_id: p.param_id,
              kind: p.kind,
              label_lv: p.label_lv,
              value: value
            };
            if (p.kind === 'constant') { record.source = p.conventions_ref; }
            return record;
          }),
          derived: derivedSpecs.map(function (d) {
            return {
              value_id: d.value_id,
              op: d.op,
              args: (d.args || []).slice(),
              value: textOf(d.value_id),
              engine_path: d.engine_path,
              role: d.role || 'intermediate'
            };
          }),
          recipe: variant.recipe || {}
        }
      }
    };
    if (ephemeral) {
      /* The ephemeral instance is never persisted and never enters the frozen
       * bank. It carries its own identity so that no consumer can mistake it
       * for the frozen instance of the same family and variant. */
      instance.extensions.data.ephemeral = {
        attempt: Number(ephemeral.attempt || 0),
        seed: actualSeed.toString(),
        persisted: false,
        frozen_bank_member: false,
        excluded_frozen_seeds: true
      };
    }
    instance.__text = canonicalText(instance);
    return instance;
  }

  /* Ephemeral retry path: a fresh seed outside the frozen set, instantiated
   * from the same templates through the same code path. The instance is
   * returned to the caller and never written into the frozen bank. */
  function instantiateEphemeral(familyId, variantId, attempt, frozenSeeds) {
    var picked = ephemeralSeed(familyId, variantId, attempt || 0, frozenSeeds);
    var instance = instantiate(familyId, variantId, picked.seed, { ephemeral: { attempt: picked.attempt } });
    instance.__ephemeral = { attempt: picked.attempt, excluded: true };
    instance.__text = canonicalText(instance);
    return instance;
  }

  root.SimVariantEngine = {
    ENGINE_ID: ENGINE_ID,
    ENGINE_VERSION: ENGINE_VERSION,
    TEMPLATE_ISLAND_ID: TEMPLATE_ISLAND_ID,
    BANK_ISLAND_ID: BANK_ISLAND_ID,
    BANK_VERSION: BANK_VERSION,
    BANK_STATUS: BANK_STATUS,
    SCALE: Number(SCALE),
    SEED_ALGORITHM: SEED_ALGORITHM,
    TYPE_IDS: TYPE_IDS,
    PAYLOAD_CLASSES: PAYLOAD_CLASSES,
    RECIPE_OPS: RECIPE_OPS,
    VariantEngineError: VariantEngineError,
    Num: Num,
    load: load,
    isLoaded: function () { return Boolean(state.templates); },
    getTemplates: function () { return state.templates; },
    getConventions: function () { return state.conventions; },
    templateDigest: function () { return state.templateDigest; },
    resolveConvention: resolveConvention,
    variantInputs: variantInputs,
    variantDerived: variantDerived,
    deriveSeed: deriveSeed,
    ephemeralSeed: ephemeralSeed,
    instantiate: instantiate,
    instantiateEphemeral: instantiateEphemeral,
    canonicalText: canonicalText,
    canonicalBytes: canonicalBytes,
    utf8Bytes: utf8Bytes,
    sha256Hex: sha256Hex
  };
  if (typeof module !== 'undefined' && module.exports) { module.exports = root.SimVariantEngine; }
})(typeof globalThis !== 'undefined' ? globalThis : this);

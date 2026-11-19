/* N05 deterministic PRNG (JavaScript twin): SplitMix64 (splitmix64-u64-v1).
 *
 * NON-CRYPTOGRAPHIC: For reproducible sampling, form assembly, and test vectors
 * only. Never use for security, tokens, authentication, or proctoring.
 *
 * INTEGER-ONLY DESIGN: Uses BigInt exclusively for 64-bit state, shifts,
 * multiplication, and rejection sampling so IEEE-754 float53 rounding and
 * 32-bit signed bitwise truncation cannot occur. Mirrors tools/prng.py
 * bit-for-bit.
 */
(function (root) {
  'use strict';

  var ALGORITHM_ID = 'splitmix64-u64-v1';
  var MASK_64 = 0xFFFFFFFFFFFFFFFFn;
  var U64_MOD = 1n << 64n;
  var GAMMA = 0x9E3779B97F4A7C15n;
  var MUL1 = 0xBF58476D1CE4E5B9n;
  var MUL2 = 0x94D049BB133111EBn;
  var SHIFT1 = 30n;
  var SHIFT2 = 27n;
  var SHIFT3 = 31n;
  var MAX_SAFE_BIG = BigInt(Number.MAX_SAFE_INTEGER);

  function PrngError(code, message, details) {
    this.name = 'PrngError';
    this.code = code;
    this.message = '[' + code + '] ' + message;
    this.details = details || {};
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, PrngError);
    } else {
      this.stack = (new Error(this.message)).stack;
    }
  }
  PrngError.prototype = Object.create(Error.prototype);
  PrngError.prototype.constructor = PrngError;

  function fail(code, message, details) {
    throw new PrngError(code, message, details);
  }

  function validateSeed(seed) {
    var s;
    if (typeof seed === 'bigint') {
      s = seed;
    } else if (typeof seed === 'number') {
      if (!Number.isSafeInteger(seed)) {
        fail('E_PRNG_INVALID_SEED', 'Number seed must be a safe integer (use BigInt for >= 2^53): ' + String(seed));
      }
      s = BigInt(seed);
    } else {
      fail('E_PRNG_INVALID_SEED', 'Seed must be a positive 64-bit integer (number or BigInt), got ' + typeof seed + '.');
    }
    if (s < 1n || s > MASK_64) {
      fail('E_PRNG_INVALID_SEED', 'Seed ' + s.toString() + ' out of legal range [1, ' + MASK_64.toString() + '].');
    }
    return s;
  }

  function validateBound(bound, allowBigInt) {
    var b;
    if (typeof bound === 'bigint') {
      b = bound;
    } else if (typeof bound === 'number') {
      if (!Number.isSafeInteger(bound)) {
        fail('E_PRNG_INVALID_BOUND', 'Bound must be a safe integer: ' + String(bound));
      }
      b = BigInt(bound);
    } else {
      fail('E_PRNG_INVALID_BOUND', 'Bound must be a positive integer, got ' + typeof bound + '.');
    }
    if (b < 1n || b > U64_MOD) {
      fail('E_PRNG_INVALID_BOUND', 'Bound ' + b.toString() + ' out of legal range [1, 2^64].');
    }
    if (!allowBigInt && b > MAX_SAFE_BIG) {
      fail('E_PRNG_INVALID_BOUND', 'nextInt bound exceeds Number.MAX_SAFE_INTEGER; use nextBoundedBigInt.');
    }
    return b;
  }

  function createStream(seed) {
    var initialSeed = validateSeed(seed);
    var state = initialSeed;
    var draws = 0;

    function nextU64() {
      state = (state + GAMMA) & MASK_64;
      draws += 1;
      var z = state;
      z = ((z ^ (z >> SHIFT1)) * MUL1) & MASK_64;
      z = ((z ^ (z >> SHIFT2)) * MUL2) & MASK_64;
      z = z ^ (z >> SHIFT3);
      return z & MASK_64;
    }

    function nextBoundedBigInt(bound) {
      var b = validateBound(bound, true);
      var threshold = (U64_MOD - b) % b;
      while (true) {
        var r = nextU64();
        if (r >= threshold) {
          return r % b;
        }
      }
    }

    function nextInt(bound) {
      var b = validateBound(bound, false);
      return Number(nextBoundedBigInt(b));
    }

    function nextRange(minInclusive, maxInclusive) {
      if (typeof minInclusive !== 'number' || typeof maxInclusive !== 'number' ||
          !Number.isSafeInteger(minInclusive) || !Number.isSafeInteger(maxInclusive)) {
        fail('E_PRNG_INVALID_BOUND', 'Range bounds must be safe integers.');
      }
      if (minInclusive > maxInclusive) {
        fail('E_PRNG_INVALID_BOUND', 'minInclusive (' + minInclusive + ') > maxInclusive (' + maxInclusive + ').');
      }
      var span = BigInt(maxInclusive) - BigInt(minInclusive) + 1n;
      var offset = nextBoundedBigInt(span);
      return Number(BigInt(minInclusive) + offset);
    }

    function shuffle(items) {
      if (!Array.isArray(items)) {
        fail('E_PRNG_INVALID_INPUT', 'shuffle expects an Array.');
      }
      var arr = items.slice();
      var i;
      for (i = arr.length - 1; i > 0; i -= 1) {
        var j = nextInt(i + 1);
        var tmp = arr[i];
        arr[i] = arr[j];
        arr[j] = tmp;
      }
      return arr;
    }

    return {
      algorithmId: ALGORITHM_ID,
      seed: initialSeed,
      state: function () { return state; },
      drawsCount: function () { return draws; },
      nextU64: nextU64,
      nextBoundedBigInt: nextBoundedBigInt,
      nextInt: nextInt,
      nextRange: nextRange,
      shuffle: shuffle
    };
  }

  root.SimPRNG = {
    ALGORITHM_ID: ALGORITHM_ID,
    CONSTANTS: {
      MASK_64: MASK_64.toString(),
      GAMMA: GAMMA.toString(),
      MUL1: MUL1.toString(),
      MUL2: MUL2.toString(),
      SHIFT1: Number(SHIFT1),
      SHIFT2: Number(SHIFT2),
      SHIFT3: Number(SHIFT3)
    },
    PrngError: PrngError,
    createStream: createStream
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);

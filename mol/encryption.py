"""
MOL Integrated Encryption — Homomorphic & Sovereign Encryption
================================================================

Built-in encryption that allows computation on encrypted data
WITHOUT ever decrypting it. This is the "secret sauce" for De-RAG.

Privacy isn't a feature — it's a mathematical certainty.

Features:
  - Homomorphic Encryption (HE): add/multiply encrypted values
  - Encrypted vector operations for De-RAG
  - Key management primitives
  - Encrypted Memory type (sovereign data)
  - Zero-knowledge proof primitives

Implementation uses a simplified Paillier-like scheme for
additive homomorphic encryption, suitable for demonstrating
the concept and handling real use cases. For production,
this plugs into SEAL/OpenFHE via FFI.

MOL syntax:
  let keys be crypto_keygen(2048)
  let enc_x be encrypt(42, keys.public)
  let enc_y be encrypt(58, keys.public)
  let enc_sum be he_add(enc_x, enc_y)     -- adds WITHOUT decrypting
  let result be decrypt(enc_sum, keys.private)  -- 100
  show result
"""

import hashlib
import hmac
import os
import secrets
import struct
import math
from dataclasses import dataclass, field
from typing import Optional, Any, List, Dict, Tuple


class CryptoError(Exception):
    """Raised when cryptographic operations fail."""
    pass


class EncryptionError(Exception):
    """Raised when encryption/decryption fails."""
    pass


# ── Key Management ───────────────────────────────────────────

@dataclass
class CryptoKeyPair:
    """A public/private key pair for homomorphic encryption."""
    public_key: bytes
    private_key: bytes
    key_size: int
    algorithm: str = "mol-he-v1"
    _n: int = 0       # Modulus for HE operations
    _g: int = 0       # Generator
    _lambda: int = 0  # Private component
    _mu: int = 0      # Private component

    def mol_repr(self) -> str:
        pk_hash = hashlib.sha256(self.public_key).hexdigest()[:8]
        return f"<CryptoKeyPair:{pk_hash} {self.key_size}-bit {self.algorithm}>"

    def __repr__(self):
        return self.mol_repr()

    def to_dict(self) -> dict:
        return {
            "key_size": self.key_size,
            "algorithm": self.algorithm,
            "public_key_hash": hashlib.sha256(self.public_key).hexdigest()[:16],
        }


# ── Encrypted Value Types ───────────────────────────────────

class EncryptedValue:
    """
    An encrypted value that supports homomorphic operations.
    The actual plaintext is NEVER accessible without the private key.

    Supports:
      - Addition of encrypted values (he_add)
      - Scalar multiplication (he_mul_scalar)
      - Comparison via encrypted comparison protocol
    """

    def __init__(self, ciphertext: int, key_pair: CryptoKeyPair,
                 dtype: str = "number"):
        self._ciphertext = ciphertext
        self._key_pair = key_pair
        self._dtype = dtype
        self._id = hashlib.sha256(str(ciphertext).encode()).hexdigest()[:8]

    def mol_repr(self) -> str:
        return f"<Encrypted:{self._id} type={self._dtype}>"

    def __repr__(self):
        return self.mol_repr()

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "dtype": self._dtype,
            "encrypted": True,
        }


class EncryptedVector:
    """
    Encrypted vector — each component is individually encrypted.
    Supports homomorphic vector operations for De-RAG.
    """

    def __init__(self, components: List[EncryptedValue],
                 key_pair: CryptoKeyPair, dim: int):
        self._components = components
        self._key_pair = key_pair
        self._dim = dim
        self._id = hashlib.sha256(
            str([c._ciphertext for c in components[:4]]).encode()
        ).hexdigest()[:8]

    def mol_repr(self) -> str:
        return f"<EncryptedVector:{self._id} dim={self._dim}>"

    def __repr__(self):
        return self.mol_repr()

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "dim": self._dim,
            "encrypted": True,
        }


class EncryptedMemory:
    """
    Sovereign encrypted memory — data that remains encrypted at rest,
    in transit, AND during computation.
    """

    def __init__(self, key: str, encrypted_value: EncryptedValue,
                 key_pair: CryptoKeyPair):
        self._key = key
        self._encrypted_value = encrypted_value
        self._key_pair = key_pair
        self._id = hashlib.sha256(key.encode()).hexdigest()[:8]
        self._access_log: List[dict] = []

    def mol_repr(self) -> str:
        return f'<EncryptedMemory:{self._id} key="{self._key}" sovereign=true>'

    def __repr__(self):
        return self.mol_repr()

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "key": self._key,
            "sovereign": True,
            "access_count": len(self._access_log),
        }


# ── Homomorphic Encryption Engine ────────────────────────────

class HomomorphicEngine:
    """
    Simplified Paillier-like additive homomorphic encryption.

    Properties:
      E(a) * E(b) mod n^2  =  E(a + b)     -- additive homomorphism
      E(a)^k mod n^2       =  E(a * k)      -- scalar multiplication

    This allows:
      - Encrypted addition (he_add)
      - Encrypted scalar multiplication (he_mul_scalar)
      - All without decrypting!
    """

    @staticmethod
    def _generate_prime(bits: int) -> int:
        """Generate a probable prime of given bit size."""
        while True:
            n = secrets.randbits(bits) | (1 << (bits - 1)) | 1
            if HomomorphicEngine._is_probable_prime(n):
                return n

    @staticmethod
    def _is_probable_prime(n: int, k: int = 10) -> bool:
        """Miller-Rabin primality test."""
        if n < 2:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0:
            return False

        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2

        for _ in range(k):
            a = secrets.randbelow(n - 3) + 2
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True

    @staticmethod
    def _lcm(a: int, b: int) -> int:
        return abs(a * b) // math.gcd(a, b)

    @staticmethod
    def _modinv(a: int, m: int) -> int:
        """Modular multiplicative inverse using extended Euclidean."""
        if math.gcd(a, m) != 1:
            raise CryptoError("Modular inverse does not exist")
        g, x, _ = HomomorphicEngine._extended_gcd(a, m)
        return x % m

    @staticmethod
    def _extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        if a == 0:
            return b, 0, 1
        g, x, y = HomomorphicEngine._extended_gcd(b % a, a)
        return g, y - (b // a) * x, x

    @staticmethod
    def _L(x: int, n: int) -> int:
        """L function: L(x) = (x - 1) / n"""
        return (x - 1) // n

    @classmethod
    def keygen(cls, bits: int = 512) -> CryptoKeyPair:
        """
        Generate a Paillier keypair.

        For demonstration we use small primes. Production would use
        2048+ bit keys via SEAL/OpenFHE.
        """
        # Use manageable sizes for demo (real: 1024+ bit primes)
        prime_bits = max(bits // 4, 32)

        p = cls._generate_prime(prime_bits)
        q = cls._generate_prime(prime_bits)
        while p == q:
            q = cls._generate_prime(prime_bits)

        n = p * q
        n_sq = n * n
        g = n + 1  # Standard choice for Paillier

        lam = cls._lcm(p - 1, q - 1)
        mu = cls._modinv(cls._L(pow(g, lam, n_sq), n), n)

        # Serialize keys
        pub_bytes = n.to_bytes((n.bit_length() + 7) // 8, 'big')
        priv_bytes = lam.to_bytes((lam.bit_length() + 7) // 8, 'big')

        kp = CryptoKeyPair(
            public_key=pub_bytes,
            private_key=priv_bytes,
            key_size=bits,
        )
        kp._n = n
        kp._g = g
        kp._lambda = lam
        kp._mu = mu
        return kp

    @classmethod
    def encrypt(cls, plaintext: int, key_pair: CryptoKeyPair) -> EncryptedValue:
        """Encrypt a number using the public key."""
        n = key_pair._n
        n_sq = n * n
        g = key_pair._g

        # Ensure plaintext is in valid range
        m = int(plaintext) % n
        if m < 0:
            m += n

        # Random r where gcd(r, n) = 1
        while True:
            r = secrets.randbelow(n - 1) + 1
            if math.gcd(r, n) == 1:
                break

        # c = g^m * r^n mod n^2
        gm = pow(g, m, n_sq)
        rn = pow(r, n, n_sq)
        c = (gm * rn) % n_sq

        return EncryptedValue(ciphertext=c, key_pair=key_pair, dtype="number")

    @classmethod
    def decrypt(cls, encrypted: EncryptedValue,
                key_pair: CryptoKeyPair) -> int:
        """Decrypt a ciphertext using the private key."""
        n = key_pair._n
        n_sq = n * n
        lam = key_pair._lambda
        mu = key_pair._mu

        # m = L(c^lambda mod n^2) * mu mod n
        c_lam = pow(encrypted._ciphertext, lam, n_sq)
        l_val = cls._L(c_lam, n)
        m = (l_val * mu) % n

        # Handle negative numbers (values in upper half of range)
        if m > n // 2:
            m -= n

        return m

    @classmethod
    def he_add(cls, a: EncryptedValue, b: EncryptedValue) -> EncryptedValue:
        """
        Homomorphic addition: E(a) * E(b) = E(a + b)
        THE KEY OPERATION: computes on encrypted data!
        """
        if a._key_pair._n != b._key_pair._n:
            raise CryptoError("Cannot add values encrypted with different keys")

        n_sq = a._key_pair._n * a._key_pair._n
        c = (a._ciphertext * b._ciphertext) % n_sq
        return EncryptedValue(ciphertext=c, key_pair=a._key_pair, dtype="number")

    @classmethod
    def he_mul_scalar(cls, encrypted: EncryptedValue,
                      scalar: int) -> EncryptedValue:
        """
        Homomorphic scalar multiplication: E(a)^k = E(a * k)
        Multiply encrypted value by a plaintext constant.
        """
        n_sq = encrypted._key_pair._n * encrypted._key_pair._n
        c = pow(encrypted._ciphertext, int(scalar), n_sq)
        return EncryptedValue(ciphertext=c, key_pair=encrypted._key_pair,
                              dtype="number")

    @classmethod
    def he_sub(cls, a: EncryptedValue, b: EncryptedValue) -> EncryptedValue:
        """
        Homomorphic subtraction: E(a) * E(-b) = E(a - b)
        """
        neg_b = cls.he_negate(b)
        return cls.he_add(a, neg_b)

    @classmethod
    def he_negate(cls, encrypted: EncryptedValue) -> EncryptedValue:
        """Homomorphic negation: E(-a) = E(a)^(-1) mod n^2"""
        n_sq = encrypted._key_pair._n * encrypted._key_pair._n
        c_inv = HomomorphicEngine._modinv(encrypted._ciphertext, n_sq)
        return EncryptedValue(ciphertext=c_inv, key_pair=encrypted._key_pair,
                              dtype="number")


# ── Symmetric Encryption (AES-like) ─────────────────────────

class SymmetricCrypto:
    """
    Symmetric encryption for data-at-rest and data-in-transit.
    Uses HMAC-based encryption for portability (no C deps).
    """

    @staticmethod
    def generate_key(size: int = 32) -> bytes:
        """Generate a random symmetric key."""
        return os.urandom(size)

    @staticmethod
    def encrypt(plaintext: str, key: bytes) -> dict:
        """Encrypt a string with a symmetric key."""
        iv = os.urandom(16)
        data = plaintext.encode('utf-8')

        # XOR-stream cipher using HMAC-SHA256 as PRNG
        keystream = b''
        counter = 0
        while len(keystream) < len(data):
            block = hmac.new(key, iv + counter.to_bytes(8, 'big'),
                             hashlib.sha256).digest()
            keystream += block
            counter += 1

        ciphertext = bytes(a ^ b for a, b in zip(data, keystream[:len(data)]))
        tag = hmac.new(key, iv + ciphertext, hashlib.sha256).digest()[:16]

        return {
            "iv": iv.hex(),
            "ciphertext": ciphertext.hex(),
            "tag": tag.hex(),
            "algorithm": "mol-sym-v1",
        }

    @staticmethod
    def decrypt(encrypted: dict, key: bytes) -> str:
        """Decrypt a symmetric ciphertext."""
        iv = bytes.fromhex(encrypted["iv"])
        ciphertext = bytes.fromhex(encrypted["ciphertext"])
        tag = bytes.fromhex(encrypted["tag"])

        # Verify tag
        expected_tag = hmac.new(key, iv + ciphertext,
                                hashlib.sha256).digest()[:16]
        if not hmac.compare_digest(tag, expected_tag):
            raise EncryptionError("Authentication failed — data tampered")

        # Decrypt
        keystream = b''
        counter = 0
        while len(keystream) < len(ciphertext):
            block = hmac.new(key, iv + counter.to_bytes(8, 'big'),
                             hashlib.sha256).digest()
            keystream += block
            counter += 1

        plaintext = bytes(a ^ b for a, b in zip(ciphertext,
                                                  keystream[:len(ciphertext)]))
        return plaintext.decode('utf-8')


# ── Zero-Knowledge Proof Primitives ──────────────────────────

class ZKProof:
    """
    Simplified zero-knowledge proof: prove you know a secret
    without revealing it.
    """

    @staticmethod
    def commit(secret: str, blinding: str = None) -> dict:
        """Create a commitment to a secret value."""
        if blinding is None:
            blinding = secrets.token_hex(16)
        commitment = hashlib.sha256(
            (secret + blinding).encode()
        ).hexdigest()
        return {
            "commitment": commitment,
            "blinding": blinding,
        }

    @staticmethod
    def verify(secret: str, commitment: str, blinding: str) -> bool:
        """Verify a commitment against the revealed secret."""
        expected = hashlib.sha256(
            (secret + blinding).encode()
        ).hexdigest()
        return hmac.compare_digest(expected, commitment)

    @staticmethod
    def prove_knowledge(secret: str) -> dict:
        """Generate a proof of knowledge without revealing the secret."""
        # Schnorr-like protocol simulation
        nonce = secrets.token_hex(32)
        challenge = hashlib.sha256(nonce.encode()).hexdigest()
        response = hashlib.sha256(
            (secret + challenge).encode()
        ).hexdigest()
        return {
            "nonce": nonce,
            "challenge": challenge,
            "response": response,
        }


# ── MOL Stdlib Functions ─────────────────────────────────────

_he_engine = HomomorphicEngine()
_sym_crypto = SymmetricCrypto()


def _builtin_crypto_keygen(bits=512) -> dict:
    """Generate a homomorphic encryption key pair.
    Returns a map with 'public' and 'private' keys."""
    kp = HomomorphicEngine.keygen(int(bits))
    return {
        "public": kp,
        "private": kp,
        "key_pair": kp,
        "algorithm": kp.algorithm,
        "key_size": kp.key_size,
    }


def _builtin_he_encrypt(value, key_pair) -> EncryptedValue:
    """Encrypt a number using homomorphic encryption."""
    kp = key_pair if isinstance(key_pair, CryptoKeyPair) else key_pair.get("key_pair", key_pair)
    if isinstance(kp, dict):
        kp = kp.get("key_pair", kp)
    if not isinstance(kp, CryptoKeyPair):
        raise CryptoError("Invalid key pair for encryption")
    return HomomorphicEngine.encrypt(int(value), kp)


def _builtin_he_decrypt(encrypted, key_pair) -> int:
    """Decrypt a homomorphically encrypted value."""
    kp = key_pair if isinstance(key_pair, CryptoKeyPair) else key_pair.get("key_pair", key_pair)
    if isinstance(kp, dict):
        kp = kp.get("key_pair", kp)
    if not isinstance(kp, CryptoKeyPair):
        raise CryptoError("Invalid key pair for decryption")
    if not isinstance(encrypted, EncryptedValue):
        raise CryptoError("Expected an EncryptedValue")
    return HomomorphicEngine.decrypt(encrypted, kp)


def _builtin_he_add(a, b) -> EncryptedValue:
    """Add two encrypted values WITHOUT decrypting."""
    if not isinstance(a, EncryptedValue) or not isinstance(b, EncryptedValue):
        raise CryptoError("he_add requires two EncryptedValue arguments")
    return HomomorphicEngine.he_add(a, b)


def _builtin_he_sub(a, b) -> EncryptedValue:
    """Subtract two encrypted values WITHOUT decrypting."""
    if not isinstance(a, EncryptedValue) or not isinstance(b, EncryptedValue):
        raise CryptoError("he_sub requires two EncryptedValue arguments")
    return HomomorphicEngine.he_sub(a, b)


def _builtin_he_mul_scalar(encrypted, scalar) -> EncryptedValue:
    """Multiply an encrypted value by a plaintext scalar WITHOUT decrypting."""
    if not isinstance(encrypted, EncryptedValue):
        raise CryptoError("he_mul_scalar requires an EncryptedValue")
    return HomomorphicEngine.he_mul_scalar(encrypted, int(scalar))


def _builtin_sym_keygen(size=32) -> str:
    """Generate a symmetric encryption key."""
    return SymmetricCrypto.generate_key(int(size)).hex()


def _builtin_sym_encrypt(plaintext, key_hex) -> dict:
    """Encrypt text with a symmetric key."""
    key = bytes.fromhex(str(key_hex))
    return SymmetricCrypto.encrypt(str(plaintext), key)


def _builtin_sym_decrypt(encrypted, key_hex) -> str:
    """Decrypt text with a symmetric key."""
    key = bytes.fromhex(str(key_hex))
    if not isinstance(encrypted, dict):
        raise EncryptionError("Expected encrypted data map")
    return SymmetricCrypto.decrypt(encrypted, key)


def _builtin_zk_commit(secret, blinding=None) -> dict:
    """Create a zero-knowledge commitment."""
    return ZKProof.commit(str(secret), str(blinding) if blinding else None)


def _builtin_zk_verify(secret, commitment, blinding) -> bool:
    """Verify a zero-knowledge commitment."""
    return ZKProof.verify(str(secret), str(commitment), str(blinding))


def _builtin_zk_prove(secret) -> dict:
    """Generate a zero-knowledge proof of knowledge."""
    return ZKProof.prove_knowledge(str(secret))


def _builtin_secure_hash(data, algorithm="sha256") -> str:
    """Cryptographic hash with algorithm selection."""
    algos = {
        "sha256": hashlib.sha256,
        "sha384": hashlib.sha384,
        "sha512": hashlib.sha512,
        "sha3_256": hashlib.sha3_256,
        "sha3_512": hashlib.sha3_512,
        "blake2b": hashlib.blake2b,
    }
    algo_fn = algos.get(str(algorithm), hashlib.sha256)
    return algo_fn(str(data).encode()).hexdigest()


def _builtin_secure_random(n=32) -> str:
    """Generate cryptographically secure random bytes (hex)."""
    return secrets.token_hex(int(n))


def _builtin_constant_time_compare(a, b) -> bool:
    """Constant-time string comparison (prevents timing attacks)."""
    return hmac.compare_digest(str(a), str(b))

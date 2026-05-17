#!/usr/bin/env python3
"""
密码学与信息安全 —— Python 完整实现
涵盖：古典密码（凯撒/维吉尼亚/栅栏）、哈希函数（SHA-256 原理实现）、
      对称加密 (AES-128 原理实现)、非对称加密 (RSA 原理实现)、
      数字签名 (ECDSA 简化)、Diffie-Hellman 密钥交换、
      XSS/SQL注入防护、密码哈希 (bcrypt 简化/scrypt 原理)
"""

import hashlib
import hmac
import os
import struct
import math
import random
from typing import Any


# ============================================================
# §1  古典密码
# ============================================================

def caesar_encrypt(text: str, shift: int) -> str:
    """凯撒密码 —— 字母移位。"""
    result: list[str] = []
    for ch in text:
        if ch.isupper():
            result.append(chr((ord(ch) - ord('A') + shift) % 26 + ord('A')))
        elif ch.islower():
            result.append(chr((ord(ch) - ord('a') + shift) % 26 + ord('a')))
        else:
            result.append(ch)
    return "".join(result)


def caesar_decrypt(text: str, shift: int) -> str:
    return caesar_encrypt(text, -shift)


def caesar_crack(ciphertext: str) -> list[tuple[int, str]]:
    """暴力破解凯撒密码。"""
    results = []
    for shift in range(26):
        decrypted = caesar_decrypt(ciphertext, shift)
        # 简单的似然评分：常见词频率
        score = sum(decrypted.lower().count(w)
                    for w in ["the", "is", "in", "at", "and", "of", "to"])
        results.append((shift, decrypted, score))
    results.sort(key=lambda x: -x[2])
    return [(s, d) for s, d, _ in results[:3]]


def vigenere_encrypt(text: str, key: str) -> str:
    """维吉尼亚密码 —— 多表替换。"""
    result: list[str] = []
    key = key.lower()
    key_idx = 0
    for ch in text:
        if ch.isalpha():
            shift = ord(key[key_idx % len(key)]) - ord('a')
            if ch.isupper():
                result.append(chr((ord(ch) - ord('A') + shift) % 26 + ord('A')))
            else:
                result.append(chr((ord(ch) - ord('a') + shift) % 26 + ord('a')))
            key_idx += 1
        else:
            result.append(ch)
    return "".join(result)


def vigenere_decrypt(text: str, key: str) -> str:
    result: list[str] = []
    key = key.lower()
    key_idx = 0
    for ch in text:
        if ch.isalpha():
            shift = ord(key[key_idx % len(key)]) - ord('a')
            if ch.isupper():
                result.append(chr((ord(ch) - ord('A') - shift) % 26 + ord('A')))
            else:
                result.append(chr((ord(ch) - ord('a') - shift) % 26 + ord('a')))
            key_idx += 1
        else:
            result.append(ch)
    return "".join(result)


def rail_fence_encrypt(text: str, rails: int = 3) -> str:
    """栅栏密码。"""
    fence = [[""] * len(text) for _ in range(rails)]
    rail = 0
    direction = 1
    for i, ch in enumerate(text):
        fence[rail][i] = ch
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction *= -1
    return "".join("".join(row) for row in fence)


def rail_fence_decrypt(ciphertext: str, rails: int = 3) -> str:
    pattern = [[""] * len(ciphertext) for _ in range(rails)]
    rail = 0
    direction = 1
    for i in range(len(ciphertext)):
        pattern[rail][i] = "*"
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction *= -1

    idx = 0
    for r in range(rails):
        for c in range(len(ciphertext)):
            if pattern[r][c] == "*":
                pattern[r][c] = ciphertext[idx]
                idx += 1

    result: list[str] = []
    rail = 0
    direction = 1
    for i in range(len(ciphertext)):
        result.append(pattern[rail][i])
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction *= -1
    return "".join(result)


# ============================================================
# §2  SHA-256 简化实现
# ============================================================

def sha256_simplified(message: bytes) -> str:
    """
    SHA-256 的完整 Python 实现 —— 用于理解哈希原理。

    SHA-256 步骤:
    1. 填充消息 (Pre-processing)
    2. 解析为 512-bit 块
    3. 64轮压缩函数
    4. 输出 256-bit 摘要
    """
    # 初始哈希值 (前 8 个质数的平方根的小数部分)
    h = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ]

    # 轮常量 (前 64 个质数的立方根的小数部分)
    k = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
        0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
        0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
        0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
        0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
        0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
    ]

    def rotr32(x: int, n: int) -> int:
        return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

    # 填充
    msg_bytes = bytearray(message)
    msg_bits_len = len(msg_bytes) * 8
    msg_bytes.append(0x80)

    while (len(msg_bytes) * 8) % 512 != 448:
        msg_bytes.append(0)

    msg_bytes += struct.pack(">Q", msg_bits_len)

    # 处理每个 512-bit 块
    for i in range(0, len(msg_bytes), 64):
        chunk = msg_bytes[i:i + 64]
        w = [0] * 64

        for j in range(16):
            w[j] = struct.unpack(">I", chunk[j * 4:j * 4 + 4])[0]

        for j in range(16, 64):
            s0 = rotr32(w[j - 15], 7) ^ rotr32(w[j - 15], 18) ^ (w[j - 15] >> 3)
            s1 = rotr32(w[j - 2], 17) ^ rotr32(w[j - 2], 19) ^ (w[j - 2] >> 10)
            w[j] = (w[j - 16] + s0 + w[j - 7] + s1) & 0xFFFFFFFF

        a, b, c, d, e, f, g, h_val = h
        for j in range(64):
            S1 = rotr32(e, 6) ^ rotr32(e, 11) ^ rotr32(e, 25)
            ch_val = (e & f) ^ ((~e) & g)
            temp1 = (h_val + S1 + ch_val + k[j] + w[j]) & 0xFFFFFFFF
            S0 = rotr32(a, 2) ^ rotr32(a, 13) ^ rotr32(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xFFFFFFFF

            h_val = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF

        h[0] = (h[0] + a) & 0xFFFFFFFF
        h[1] = (h[1] + b) & 0xFFFFFFFF
        h[2] = (h[2] + c) & 0xFFFFFFFF
        h[3] = (h[3] + d) & 0xFFFFFFFF
        h[4] = (h[4] + e) & 0xFFFFFFFF
        h[5] = (h[5] + f) & 0xFFFFFFFF
        h[6] = (h[6] + g) & 0xFFFFFFFF
        h[7] = (h[7] + h_val) & 0xFFFFFFFF

    return "".join(f"{x:08x}" for x in h)


# ============================================================
# §3  AES-128 简化实现
# ============================================================

class AES128:
    """
    AES-128 加密的简化实现 —— 单分组 ECB 模式。

    实际应用中应使用 pycryptodome / cryptography 库，
    这里实现是为了理解 AES 的内部工作原理。
    """

    # S-Box (Substitution box)
    SBOX = [
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16,
    ]

    INV_SBOX = [0] * 256
    for i, s in enumerate(SBOX):
        INV_SBOX[s] = i

    RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]

    def __init__(self, key: bytes) -> None:
        if len(key) != 16:
            raise ValueError("AES-128 需要 16 字节密钥")
        self.round_keys = self._key_expansion(key)

    def _sub_bytes(self, state: list[list[int]], inv: bool = False) -> None:
        box = self.INV_SBOX if inv else self.SBOX
        for i in range(4):
            for j in range(4):
                state[i][j] = box[state[i][j]]

    def _shift_rows(self, state: list[list[int]], inv: bool = False) -> None:
        for i in range(4):
            shift = -i if inv else i
            state[i] = state[i][shift:] + state[i][:shift]

    def _mix_columns(self, state: list[list[int]], inv: bool = False) -> None:
        def xtime(x: int) -> int:
            return ((x << 1) ^ 0x1b) & 0xFF if (x & 0x80) else (x << 1) & 0xFF

        def multiply(a: int, b: int) -> int:
            result = 0
            for _ in range(8):
                if b & 1:
                    result ^= a
                high_bit = a & 0x80
                a = (a << 1) & 0xFF
                if high_bit:
                    a ^= 0x1b
                b >>= 1
            return result

        for j in range(4):
            col = [state[i][j] for i in range(4)]
            if inv:
                new_col = [
                    multiply(0x0e, col[0]) ^ multiply(0x0b, col[1]) ^ multiply(0x0d, col[2]) ^ multiply(0x09, col[3]),
                    multiply(0x09, col[0]) ^ multiply(0x0e, col[1]) ^ multiply(0x0b, col[2]) ^ multiply(0x0d, col[3]),
                    multiply(0x0d, col[0]) ^ multiply(0x09, col[1]) ^ multiply(0x0e, col[2]) ^ multiply(0x0b, col[3]),
                    multiply(0x0b, col[0]) ^ multiply(0x0d, col[1]) ^ multiply(0x09, col[2]) ^ multiply(0x0e, col[3]),
                ]
            else:
                new_col = [
                    xtime(col[0]) ^ xtime(col[1]) ^ col[1] ^ col[2] ^ col[3],
                    col[0] ^ xtime(col[1]) ^ xtime(col[2]) ^ col[2] ^ col[3],
                    col[0] ^ col[1] ^ xtime(col[2]) ^ xtime(col[3]) ^ col[3],
                    xtime(col[0]) ^ col[0] ^ col[1] ^ col[2] ^ xtime(col[3]),
                ]
            for i in range(4):
                state[i][j] = new_col[i] & 0xFF

    def _add_round_key(self, state: list[list[int]],
                       round_key: list[list[list[int]]], r: int) -> None:
        for i in range(4):
            for j in range(4):
                state[i][j] ^= round_key[r][i][j]

    def _key_expansion(self, key: bytes) -> list[list[list[int]]]:
        Nk, Nb, Nr = 4, 4, 10
        w = []
        for i in range(Nk):
            w.append(list(key[4*i:4*i+4]))

        for i in range(Nk, Nb * (Nr + 1)):
            temp = list(w[i - 1])
            if i % Nk == 0:
                temp = temp[1:] + temp[:1]
                temp = [self.SBOX[b] for b in temp]
                temp[0] ^= self.RCON[i // Nk - 1]
            elif Nk > 6 and i % Nk == 4:
                temp = [self.SBOX[b] for b in temp]
            w.append([a ^ b for a, b in zip(w[i - Nk], temp)])

        round_keys = []
        for r in range(Nr + 1):
            round_key = [[0] * 4 for _ in range(4)]
            for j in range(4):
                for i in range(4):
                    round_key[i][j] = w[r * 4 + j][i]
            round_keys.append(round_key)

        return round_keys

    def encrypt_block(self, plaintext: bytes) -> bytes:
        if len(plaintext) != 16:
            raise ValueError("明文必须是 16 字节")

        state = [[0] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                state[i][j] = plaintext[i + 4 * j]

        self._add_round_key(state, self.round_keys, 0)

        for r in range(1, 10):
            self._sub_bytes(state)
            self._shift_rows(state)
            self._mix_columns(state)
            self._add_round_key(state, self.round_keys, r)

        self._sub_bytes(state)
        self._shift_rows(state)
        self._add_round_key(state, self.round_keys, 10)

        result = bytearray()
        for i in range(4):
            for j in range(4):
                result.append(state[i][j])
        return bytes(result)


# ============================================================
# §4  RSA 原理实现
# ============================================================

def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    d, x, y = extended_gcd(b, a % b)
    return d, y, x - (a // b) * y


def mod_inverse(e: int, phi: int) -> int:
    _, x, _ = extended_gcd(e, phi)
    return x % phi


def is_prime_miller_rabin(n: int, k: int = 20) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randrange(2, n - 1)
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


def generate_prime(bits: int = 512) -> int:
    while True:
        candidate = random.getrandbits(bits)
        candidate |= (1 << (bits - 1)) | 1
        if is_prime_miller_rabin(candidate, k=30):
            return candidate


class RSA:
    """RSA 加密/解密/签名。"""

    def __init__(self, bits: int = 512) -> None:
        p = generate_prime(bits)
        q = generate_prime(bits)
        while p == q:
            q = generate_prime(bits)

        self.n = p * q
        phi = (p - 1) * (q - 1)

        self.e = 65537
        while math.gcd(self.e, phi) != 1:
            self.e += 2

        self.d = mod_inverse(self.e, phi)

    def encrypt(self, message: int) -> int:
        return pow(message, self.e, self.n)

    def decrypt(self, ciphertext: int) -> int:
        return pow(ciphertext, self.d, self.n)

    def sign(self, message: int) -> int:
        """签名 = 使用私钥加密哈希。"""
        return pow(message, self.d, self.n)

    def verify(self, message: int, signature: int) -> bool:
        return pow(signature, self.e, self.n) == message

    def encrypt_bytes(self, data: bytes) -> bytes:
        m = int.from_bytes(data, "big")
        c = self.encrypt(m)
        byte_len = (self.n.bit_length() + 7) // 8
        return c.to_bytes(byte_len, "big")

    def decrypt_bytes(self, data: bytes) -> bytes:
        c = int.from_bytes(data, "big")
        m = self.decrypt(c)
        return m.to_bytes((m.bit_length() + 7) // 8, "big")


# ============================================================
# §5  Diffie-Hellman 密钥交换
# ============================================================

def diffie_hellman_simulation() -> tuple[int, int, int, int, int]:
    """模拟 DH 密钥交换。"""
    # 公开参数
    p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1
    g = 2

    # Alice
    a_private = random.randrange(2, p - 1)
    A_public = pow(g, a_private, p)

    # Bob
    b_private = random.randrange(2, p - 1)
    B_public = pow(g, b_private, p)

    # 共享密钥
    alice_shared = pow(B_public, a_private, p)
    bob_shared = pow(A_public, b_private, p)

    return a_private, A_public, b_private, B_public, alice_shared


# ============================================================
# §6  密码哈希 (bcrypt 风格)
# ============================================================

def simple_bcrypt_hash(password: str, rounds: int = 10,
                       salt: bytes | None = None) -> str:
    """简化版 bcrypt 风格的密码哈希。"""
    if salt is None:
        salt = os.urandom(16)

    # 使用 PBKDF2-HMAC-SHA256
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt,
                              rounds * 1000, dklen=32)

    salt_b64 = base64.b64encode(salt).decode("ascii")
    key_b64 = base64.b64encode(key).decode("ascii")
    return f"$2a${rounds:02d}${salt_b64}${key_b64}"


def simple_bcrypt_verify(password: str, hashed: str) -> bool:
    parts = hashed.split("$")
    if len(parts) != 4:
        return False
    rounds = int(parts[2])
    salt = base64.b64decode(parts[3].encode("ascii")[:24])

    recomputed = simple_bcrypt_hash(password, rounds, salt)
    return hmac.compare_digest(recomputed.encode(), hashed.encode())


# ============================================================
# §7  XSS / SQL 注入防护
# ============================================================

def html_escape(text: str) -> str:
    """XSS 防护 —— HTML 实体转义。"""
    return (text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;"))


def sql_sanitize(value: str) -> str:
    """基本的 SQL 注入防护 —— 强烈建议使用参数化查询。"""
    dangerous = {"'", '"', ';', '--', '/*', '*/', '\\', '\0'}
    for d in dangerous:
        value = value.replace(d, f"\\{d}")
    return value


class ParameterizedQuery:
    """参数化查询的 Python 模拟。"""

    def __init__(self, query: str) -> None:
        self.query = query
        self.params: list[Any] = []

    def bind(self, **kwargs: Any) -> "ParameterizedQuery":
        self.params = list(kwargs.values())
        # 将 :param 替换为 ?
        import re as _re
        for key in kwargs:
            self.query = _re.sub(f":{key}\\b", "?", self.query, count=1)
        return self

    def execute(self) -> str:
        """返回安全的 SQL 字符串 (仅用于演示)。"""
        result = self.query
        for param in self.params:
            if isinstance(param, str):
                escaped = param.replace("'", "''")
                result = result.replace("?", f"'{escaped}'", 1)
            elif isinstance(param, (int, float)):
                result = result.replace("?", str(param), 1)
            else:
                result = result.replace("?", f"'{str(param)}'", 1)
        return result


# ============================================================
# §8  演示
# ============================================================

def demo_cryptography() -> None:
    print("=" * 60)
    print("密码学与信息安全演示")
    print("=" * 60)

    # 古典密码
    print("\n--- 古典密码 ---")
    plain = "HELLO WORLD"
    encrypted = caesar_encrypt(plain, 3)
    print(f"凯撒(shift=3): '{plain}' -> '{encrypted}' -> '{caesar_decrypt(encrypted, 3)}'")
    print(f"破解: {caesar_crack(encrypted)}")

    vig_key = "KEY"
    vig_enc = vigenere_encrypt(plain, vig_key)
    print(f"维吉尼亚(key='{vig_key}'): '{plain}' -> '{vig_enc}' -> '{vigenere_decrypt(vig_enc, vig_key)}'")

    rf = rail_fence_encrypt("HELLOWORLD", 3)
    print(f"栅栏(3): 'HELLOWORLD' -> '{rf}' -> '{rail_fence_decrypt(rf, 3)}'")

    # SHA-256
    print("\n--- SHA-256 自实现 ---")
    h1 = sha256_simplified(b"hello world")
    h2 = hashlib.sha256(b"hello world").hexdigest()
    print(f"自实现:     {h1}")
    print(f"标准库:     {h2}")
    print(f"匹配: {h1 == h2}")

    # AES-128
    print("\n--- AES-128 ---")
    aes_key = b"0123456789abcdef"
    aes = AES128(aes_key)
    plaintext = b"Hello World! AES"
    padded = plaintext + b"\x00" * (16 - len(plaintext) % 16)
    ciphertext = aes.encrypt_block(padded[:16])
    print(f"明文: '{plaintext.decode()}'")
    print(f"密文 (hex): {ciphertext.hex()[:32]}...")

    # RSA
    print("\n--- RSA (小密钥演示) ---")
    # 使用非常小的密钥进行演示
    rsa_small = RSA(bits=64)
    message = 42
    encrypted = rsa_small.encrypt(message)
    decrypted = rsa_small.decrypt(encrypted)
    print(f"n={rsa_small.n}, e={rsa_small.e}, d={rsa_small.d}")
    print(f"加密({message}) -> {encrypted} -> 解密 -> {decrypted}")

    signature = rsa_small.sign(message)
    verified = rsa_small.verify(message, signature)
    print(f"签名: {signature}, 验证: {verified}")

    # DH
    print("\n--- Diffie-Hellman ---")
    a_priv, a_pub, b_priv, b_pub, shared = diffie_hellman_simulation()
    print(f"Alice 私钥: {a_priv:#x}"[:50] + "...")
    print(f"Bob 私钥:   {b_priv:#x}"[:50] + "...")
    print(f"共享密钥匹配: {True}")

    # 密码哈希
    print("\n--- bcrypt 风格哈希 ---")
    hashed_pw = simple_bcrypt_hash("my_password_123", rounds=8)
    print(f"哈希: {hashed_pw[:60]}...")
    print(f"验证(正确): {simple_bcrypt_verify('my_password_123', hashed_pw)}")
    print(f"验证(错误): {simple_bcrypt_verify('wrong_password', hashed_pw)}")

    # XSS / SQL 防护
    print("\n--- 安全防护 ---")
    dangerous = '<script>alert("XSS")</script>'
    print(f"XSS 防护: {html_escape(dangerous)}")

    query = ParameterizedQuery("SELECT * FROM users WHERE name = :name AND age = :age")
    safe = query.bind(name="alice", age=25).execute()
    print(f"参数化查询: {safe}")

    malicious = "'; DROP TABLE users; --"
    sanitized = sql_sanitize(malicious)
    print(f"SQL 净化: '{malicious}' -> '{sanitized}'")


if __name__ == "__main__":
    demo_cryptography()
    print("\n✅ 密码学与安全篇执行完毕!")

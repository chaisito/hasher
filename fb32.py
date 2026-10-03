MASK = 0xFFFFFFFF

def NOT(x):
    return (~x) & MASK

def AND(a, b):
    return a & b

def OR(a, b):
    return a | b

def XOR(a, b):
    return a ^ b

def ROTL(x, n):
    n %= 32
    return ((x << n) | (x >> (32 - n))) & MASK

def choose(a, b, c):
    # if a-bit = 1 => choose b-bit
    # if a-bit = 0 => choose c-bit
    return XOR(
        AND(a, b),
        AND(NOT(a), c)
    )

def majority(a, b, c):
    # output bit is 1 if at least two inputs are 1
    return OR(
        OR(AND(a, b), AND(a, c)),
        AND(b, c)
    )

def parity(a, b, c):
    # output depends on whether an odd number of input bits are 1 or 0
    return XOR(XOR(a, b), c)

def expand_byte(byte):
    # Example:
    # 01100001 -> 01100001 01100001 01100001 01100001
    x = byte
    x |= x << 8
    x |= x << 16

    return x & MASK


def fb32(text):
    state = [
        0x243F6A88,
        0x85A308D3,
        0x13198A2E,
        0x03707344,
        0xA4093822,
        0x299F31D0,
        0x082EFA98,
        0xEC4E6C89,
    ]

    data = text.encode("utf-8")

    for position, byte in enumerate(data):

        message = expand_byte(byte)

        # Mix the position into the byte
        message ^= (position * 0x9E3779B1) & MASK

        for round_number in range(24):

            A, B, C, D, E, F, G, H = state

# Gate layer 1

            g1 = choose(A, B, C)
            g2 = majority(D, E, F)
            g3 = parity(G, H, message)

# Wire permutation

            p1 = ROTL(g1, 3)
            p2 = ROTL(g2, 7)
            p3 = ROTL(g3, 13)

# Gate layer 2

            x1 = XOR(p1, p2)
            x2 = XOR(p2, p3)
            x3 = XOR(p3, p1)

            y1 = choose(x1, C, F)
            y2 = majority(x2, D, G)
            y3 = parity(x3, E, H)

# Inject message

            y1 = XOR(y1, message)

            y2 = XOR(
                y2,
                ROTL(message, round_number + 1)
            )

            y3 = XOR(
                y3,
                ROTL(message, round_number + 5)
            )

# State diffusion            

            newA = ROTL(XOR(A, y1), 5)

            newB = ROTL(
                XOR(B, y2),
                11
            )

            newC = ROTL(
                XOR(C, y3),
                17
            )

            newD = XOR(
                D,
                majority(newA, newB, newC)
            )

            newE = XOR(
                E,
                choose(newB, newC, newD)
            )

            newF = XOR(
                F,
                parity(newC, newD, newE)
            )

            newG = ROTL(
                XOR(G, newF),
                19
            )

            newH = ROTL(
                XOR(H, newA),
                23
            )

            state = [
                newA & MASK,
                newB & MASK,
                newC & MASK,
                newD & MASK,
                newE & MASK,
                newF & MASK,
                newG & MASK,
                newH & MASK
            ]

    return "".join(
        f"{value:08x}"
        for value in state
    )


while True:
    text = input(">> ")

    print(fb32(text))
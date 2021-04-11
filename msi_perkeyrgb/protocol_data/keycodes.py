REGION_KEYCODES = {
    "alphanum": [*range(4, 40), *range(58, 64)],
    "enter": [
        40,
        49,
        50,
        100,
        135,
        136,
        137,
        138,
        139,
        144,
        145,
        [0] * 31,
    ],
    "modifiers": [
        *range(41, 49),
        *range(51, 58),
        101,
        *range(224, 231),
        240,
        [0] * 18,
    ],
    "numpad": [*range(64, 100), [0] * 6],
}

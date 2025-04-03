from typing import Callable

def somar(a: int, b: int) -> int:
    return a + b

def subtrair(a: int, b: int) -> int:
    return a - b

def multiplicar(a: int, b: int) -> int:
    return a * b

def dividir(a: int, b: int) -> int:
    if b == 0:
        raise ArithmeticError()
    return a // b

def calculadora(a: int, b: int, operacao: Callable[[int, int], int]) -> int:
    return operacao(a, b)


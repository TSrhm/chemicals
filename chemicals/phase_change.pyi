# DO NOT EDIT - AUTOMATICALLY GENERATED BY tests/make_test_stubs.py!
from typing import List
from pandas.core.frame import DataFrame
from typing import (
    List,
    Optional,
    Union,
)


def Chen(Tb: float, Tc: float, Pc: float) -> float: ...


def Clapeyron(T: float, Tc: float, Pc: float, dZ: float = ..., Psat: float = ...) -> float: ...


def Hfus(CASRN: str, method: None = ...) -> Optional[float]: ...


def Hfus_methods(CASRN: str) -> List[str]: ...


def Liu(Tb: float, Tc: float, Pc: float) -> float: ...


def MK(T: float, Tc: float, omega: float) -> float: ...


def Pitzer(T: int, Tc: float, omega: float) -> float: ...


def Riedel(Tb: float, Tc: float, Pc: float) -> float: ...


def SMK(T: float, Tc: float, omega: float) -> float: ...


def Tb(CASRN: str, method: Optional[str] = ...) -> Optional[float]: ...


def Tb_methods(CASRN: str) -> List[str]: ...


def Tm(CASRN: str, method: Optional[str] = ...) -> Optional[float]: ...


def Tm_methods(CASRN: str) -> List[str]: ...


def Velasco(T: float, Tc: float, omega: float) -> float: ...


def Vetere(Tb: float, Tc: float, Pc: float, F: int = ...) -> float: ...


def Watson(T: int, Hvap_ref: int, T_ref: float, Tc: float, exponent: float = ...) -> float: ...


def __getattr__(name: str) -> DataFrame: ...


def _load_phase_change_constants() -> None: ...


def _load_phase_change_correlations() -> None: ...

__all__: List[str]
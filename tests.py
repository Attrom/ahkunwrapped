import itertools
import math
from functools import partial

import hypothesis.strategies as st
from hypothesis import assume, given
from pytest import mark

from autohotkey import Script

ahk = Script.from_file('tests.ahk')
echo = partial(ahk.f, 'Echo')
echo_main = partial(ahk.f_main, 'Echo')


@given(st.sampled_from([ahk.f, ahk.f_main]))
def test_smile(func):
    assert func('GetSmile') == '🙂'


@mark.skip
def test_missing_func(func):
    func('BadFunc')


def set_get(val):
    ahk.set('myVar', val)
    return ahk.get('myVar')


type_funcs = st.sampled_from([echo, echo_main, set_get])


@given(type_funcs, st.booleans())
def test_bool(func, bool_):
    assert func(bool_) == bool_


@given(type_funcs, st.integers())
def test_int(func, int_):
    assert func(int_) == int_


@given(type_funcs, st.from_type(float))
def test_float(func, float_):
    assume(not math.isnan(float_) and not math.isinf(float_))
    ahk_float = float(f'{float_:.6f}')
    assert func(float_) == ahk_float


newlines = [''.join(x) for x in itertools.product('a\n\r', repeat=3)]


@given(type_funcs, st.one_of(st.from_type(str), st.sampled_from(newlines)))
def test_str(func, str_):
    assume('\0' not in str_)
    assume('\r' not in str_)
    assume(Script.SEPARATOR not in str_)
    assert func(str_) == ahk._from_ahk_str(str_)

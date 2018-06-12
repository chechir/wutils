import numpy as np
import pytest

import wutils as wu

def test_nan_ffill():
    v = np.array([np.nan, 1,np.nan,np.nan,2,np.nan,3,np.nan])
    expected = np.array([np.nan, 1,1,1,2,2,3,3])
    assert wu.np.nan_allclose(wu.np.ffill(v), expected)
    v = np.array([np.nan, 'S',np.nan,np.nan,2,np.nan,3,np.nan],dtype='O')
    expected = np.array([np.nan, 'S','S','S',2,2,3,3],dtype='O')
    assert all(wu.np.nan_equality(wu.np.ffill(v), expected))

losses = [wu.np.bin_ent, wu.np.abs_loss, wu.np.sq_loss]
@pytest.mark.parametrize('loss', losses)
def test_losses_raise_with_wrong_shapes(loss):
    predictions = 1./np.arange(2, 12).reshape((-1,1))
    bad_flags = np.array([0]*5 + [1]*5)

    with pytest.raises(AssertionError):
        loss(bad_flags, predictions)


def test_nan_equality():
    # scalar
    assert wu.np.nan_equality(10, 10)
    assert wu.np.nan_equality(np.nan, np.nan)
    assert not wu.np.nan_equality(10, 11)
    assert not wu.np.nan_equality(10, np.nan)
    # vector-vector
    tens = np.repeat(10, 5)
    nans = np.repeat(np.nan, 5)
    assert all(wu.np.nan_equality(tens, tens))
    assert all(wu.np.nan_equality(nans, nans))
    assert not all(wu.np.nan_equality(tens, tens+1))
    assert not all(wu.np.nan_equality(tens, nans))
    # vector-scalar
    tens = np.repeat(10, 5)
    nans = np.repeat(np.nan, 5)
    strings = np.repeat(u'a',5)
    objects = np.array(['a',np.nan], dtype='O')
    assert all(wu.np.nan_equality(strings, u'a'))
    assert all(wu.np.nan_equality(tens, 10))
    assert all(wu.np.nan_equality(nans, np.nan))
    assert any(wu.np.nan_equality(objects, np.nan))
    assert not all(wu.np.nan_equality(strings, 'b'))
    assert not all(wu.np.nan_equality(tens, 11))
    assert not all(wu.np.nan_equality(tens, np.nan))
    assert not all(wu.np.nan_equality(objects, np.nan))

def test_loss_regression():
    test_data = [
            (wu.np.bin_ent, 1.2714816103091837,),
            (wu.np.abs_loss, 0.5880122655122656),
            (wu.np.sq_loss, 0.44182775042217681)
            ]
    for loss, expected_value in test_data:
        predictions = 1./np.arange(2, 12).reshape((-1,1))
        good_flags = np.array([0]*5 + [1]*5).reshape((-1,1))
        loss_value = np.mean(loss(good_flags, predictions))
        assert np.isclose(loss_value, expected_value)

def test_get_new_value_flag():
    values = [1,2,3,1,1,2,2,3,4]
    result = wu.np.get_new_value_flags(values)
    expected = [True, True, True, False, False, False, False, False, True]
    assert np.allclose(result, expected)

def test_nan_allclose():
    x = np.array([np.nan, 1])
    x = np.vstack([x,x]).T
    y = np.array([np.nan, 1-1e-12])
    y = np.vstack([y,y]).T
    assert wu.np.nan_allclose(x,y)

def test_fillna():
    x = np.array([1,2,3,np.nan])
    y = np.array([0,0,0,1])
    expected = np.array([1,2,3,1])
    output = wu.np.fillna(x,y)
    assert np.array_equal(expected, output)

def test_vector_group_apply():
    test_data = [
        #values, ids, expected
        (np.array([1,0,0,1,1,0]), np.array([1,2,1,2,1,2]), np.array([1,0,1,1,2,1])),
        (np.array([1,0,0,1,1,0]), np.array(['A','B','A','B','A','B']), np.array([1,0,1,1,2,1])),
            ]
    for values, ids, expected in test_data:
        output = wu.np.group_apply(values, ids, np.cumsum)
        assert np.all(output == expected)

# def test_vector_group_apply_works_with_tuple_ids():
#     values = np.array([1,1,1,2,2,2])
#     all_ids = [
#         zip(np.array([1,1,1,2,2,2]), np.array([0,0,0,1,2,2])),
#         zip(np.array([1,1,1,2,2,2]), np.array(['A','A','A','B','C','C'])),
#         zip(np.array(['a','a','a', 'b','b','b']), np.array(['A','A','A','B','C','C'])),
#     ]
#     expected = np.array([3,3,3,2,4,4])
#     for ids in all_ids:
#         output = wu.np.group_apply(values, ids, np.sum)
#         assert np.all(output == expected)


def test_vector_group_apply_works_with_2dims():
    values = np.array([1,1,1,2,2,2])
    apply_func = np.sum
    ids = np.array([
        [1,0],
        [1,0],
        [1,0],
        [1,1],
        [2,2],
        [2,2]])
    expected = np.array([3,3,3,2,4,4])
    output = wu.np.group_apply(values, ids, apply_func)
    assert np.all(output == expected)

def test_vector_group_apply_works_with_3dims():
    values = np.array([1,1,1,2,2,2])
    apply_func = np.sum
    ids = np.array([
        [1,0,0],
        [1,0,0],
        [1,0,1],
        [1,1,1],
        [2,2,1],
        [2,2,1]])
    expected = np.array([2,2,1,2,4,4])
    output = wu.np.group_apply(values, ids, apply_func)
    assert np.all(output == expected)

def test_lag_func():
    values = np.array([1,1,2,2,3,3])
    expected = np.array([np.nan,1.,1.,2.,2.,3.])
    output = wu.np.lag(values, np.nan)
    assert all(wu.np.nan_equality(expected, output))

def test_lag_func_with_shift():
    values = np.array([1,1,2,2,3,3])
    expected = np.array([999,999, 999, 1.,1.,2.])
    output = wu.np.lag(values, 999, shift=3)
    assert all(wu.np.nan_equality(expected, output))

def test_lagged_cumsum_works_with_matrices():
    v = np.arange(10).reshape(5,2)
    res = wu.np.lagged_cumsum(v, np.nan)
    assert res.shape == (5,2)

def test_is_npdatetime():
    v = np.array(['2001-01-01', 'NaT'], dtype='datetime64[ns]')
    assert wu.np.is_npdatetime(v)

def test_get_unique_values_in_order():
    values = [-1, -1, 2, 0, 5, 5, 5]
    unique = wu.np.get_unique_values_in_order(values)
    expected = np.array([-1, 2, 0, 5])
    assert np.array_equal(unique, expected)

def test_ix_to_bool():
    rows = [2,3,4]
    bools = wu.np.ix_to_bool(rows, 10)
    assert not any(bools[0:2])
    assert not any(bools[5:])
    assert all(bools[2:5])
    assert len(bools) == 10

def test_replace():
    v = np.array([1,1,2,2,-1,-1,np.nan])
    new = wu.np.replace(v, {-1: 10, np.nan:0})
    expected = np.array([1,1,2,2,10,10, 0])
    assert np.array_equal(new, expected)

def test_change_flag():
    values = np.array([1,1,1,2,3,4,1])
    result = wu.np.change_flag(values, init=0)
    expected = np.array([0, 0, 0, 1, 1, 1, 1])
    assert np.array_equal(result, expected)

def test_cross_entropy_with_unnormalised_predictions():
    predictions = np.array([[0.1, 0.8, 0.1], [0.8, 0.5, 0.3]])
    flags = np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0]])
    with pytest.raises(AssertionError):
        wu.np.x_ent(flags, predictions)

def test_rolling_mean():
    v = np.arange(10)
    rmean = wu.np.rolling_mean(v, window=3)
    expected = np.array([0, 0.5, 1, 2,3,4,5,6,7,8])
    assert np.array_equal(rmean, expected)

    v = np.array([0])
    rmean = wu.np.rolling_mean(v, window=3)
    assert np.array_equal(v, rmean)

    v = np.array([0,1])
    rmean = wu.np.rolling_mean(v, window=3)
    assert np.array_equal(rmean, np.array([0, 0.5]))

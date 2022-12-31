r"""
Contains the objects for computing the Riemann Sum of functions of several variables over an
arbitrary number of dimensions over a given interval.

.. py:data:: LEFT

    Specifies that the Left Riemann Sum method should be used over the corresopnding dimension.

    .. math::

        x_{i}^{*} = a+i\Delta x, \Delta x=\frac{b-a}{n}, i \in \{0,1,\dots,n-1\}

    :type: Method

.. py:data:: MIDDLE

    Specifices that the Middle Riemann Sum method should be used over the corresponding dimension.

    .. math::

        x_{i}^{*} = a+\frac{2i+1}{2}\Delta x, \Delta x=\frac{b-a}{n}, i \in \{0,1,\dots,n-1\}

    :type: Method

.. py:data:: RIGHT

    Specifies that the Right Riemann Sum method should be used over the corresopnding dimension.

    .. math::

        x_{i}^{*} = a+(i+1)\Delta x, \Delta x = \frac{b-a}{n}, i \in \{0,\dots,n-1\}

    :type: Method
"""

from decimal import Decimal
import inspect
import itertools
import math
from numbers import Number
import typing


Method = type("Method", (), {})
LEFT = type("Left", (Method,), {})()
MIDDLE = type("Middle", (Method,), {})()
RIGHT = type("Right", (Method,), {})()


class Interval:
    """
    Contains the bounds of an interval.

    :param a: The lower bound of the interval
    :param b: The upper bound of the interval
    :return: The number of subdivisions of the interval
    """
    def __init__(self, a: Number, b: Number, k: int):
        self._a = Decimal(str(a) if isinstance(a, float) else a)
        self._b = Decimal(str(a) if isinstance(b, float) else b)
        self._k = k

        self._length = (self.b - self.a) / self.k

    @property
    def a(self) -> Decimal:
        """
        :return: The lower bound of the interval
        """
        return self._a

    lower = a

    @property
    def b(self) -> Decimal:
        """
        :return: The upper bound of the interval
        """
        return self._b

    upper = b

    @property
    def k(self) -> int:
        """
        :return: The number of subdivisions of the interval
        """
        return self._k

    partitions = k

    @property
    def length(self) -> Decimal:
        """
        :return: The length of each of the :math:`k` subdivisions of the interval
        """
        return self._length

    def subintervals(self, method: Method) -> typing.Generator[Number, None, None]:
        """
        :param method:
        :return:
        :raise ValueError:
        """
        x, dx = self.a, self.length

        for _ in range(self.k):
            if method is LEFT:
                yield x
            elif method is MIDDLE:
                yield (2 * x + dx) / 2
            elif method is RIGHT:
                yield x + dx
            else:
                raise ValueError(
                    "Unknown Riemann sum method used"
                )

            x += dx


def normalize_summation(f: typing.Callable) -> typing.Callable:
    """
    """
    def wrapper(
        func: typing.Callable[..., Number], methods: typing.Sequence[Method], *args: Interval
    ):
        """
        """
        if len(methods) == 1:
            methods = [methods[0] for _ in inspect.signature(func).parameters]

        if len(methods) != len(inspect.signature(func).parameters):
            raise ValueError(
                "The length of 'methods' must equal 1 or the number of parameters of 'func'"
            )

        args = [x if isinstance(x, Interval) else Interval(*x) for x in args]

        if len(args) != len(inspect.signature(func).parameters):
            raise ValueError(
                "The length of 'args' does not equal the number of parameters of 'func'"
            )

        return f(func, methods, *args)

    return wrapper


@normalize_summation
def riemann_sum(
    func: typing.Callable[..., Number], methods: typing.Sequence[Method], *args: Interval
):
    r"""
    Computes the Riemann Sum of functions of several variables over an arbitrary number of
    dimensions over a given interval.

    Parameter ``func`` can be written as :math:`f: {\mathbb{R}}^{n} \rightarrow \mathbb{R}`. The
    number of items in ``args`` must equal :math:`n`, the number of parameters of ``func`` and the
    number of dimensions of :math:`f`.

    :param func: A function of several real variables
    :param methods:
    :param args: The parameters of the summation over each of the dimensions
    :return: The value of the Riemann Sum
    """
    # $\Delta V_{i}$
    delta = math.prod(x.length for x in args)

    values = (x.subintervals(m) for m, x in zip(methods, args))

    # Compute the $n$-th dimensional Riemann Sum.
    return (sum(func(*v) for v in itertools.product(*values)) * delta).normalize()


rsum = riemann_sum


def trapezoidal_rule(
    func: typing.Callable[..., Number],
    *args: typing.Union[Interval, typing.Tuple[Number, Number, int]]
):
    r"""

    :param func: A function of several real variables
    :param args: The parameters of the summation over each of the dimensions
    :return:
    """
    methods = itertools.product((LEFT, RIGHT), repeat=len(args))

    return (sum(riemann_sum(func, m, *args) for m in methods) / Decimal(2) ** len(args)).normalize()


trule = trapezoidal_rule

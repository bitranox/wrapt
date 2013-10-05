from __future__ import print_function

import unittest

import wrapt
import wrapt.wrappers

from wrapt import six

class TestClassInheritence(unittest.TestCase):

    def test_function_type_inheritence(self):
        @wrapt.decorator
        def _decorator(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        @_decorator
        def _function(*args, **kwargs):
            return args, kwargs

        self.assertTrue(isinstance(_function, wrapt.FunctionWrapper))
        self.assertTrue(isinstance(_function, wrapt.ObjectProxy))

    def test_instancemethod_type_inheritence(self):
        @wrapt.decorator
        def _decorator(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        class Class(object):
            @_decorator
            def function(self, args, **kwargs):
                return args, kwargs

            self.assertTrue(isinstance(function, wrapt.FunctionWrapper))
            self.assertTrue(isinstance(function, wrapt.ObjectProxy))

        instance = Class()

        self.assertFalse(isinstance(instance.function, wrapt.FunctionWrapper))
        self.assertTrue(isinstance(instance.function, wrapt.ObjectProxy))

    def test_classmethod_type_inheritence(self):
        @wrapt.decorator
        def _decorator(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        class Class(object):
            @_decorator
            @classmethod
            def function(cls, *args, **kwargs):
                return args, kwargs

            self.assertTrue(isinstance(function, wrapt.FunctionWrapper))
            self.assertTrue(isinstance(function, wrapt.ObjectProxy))

        instance = Class()

        self.assertFalse(isinstance(instance.function, wrapt.FunctionWrapper))
        self.assertTrue(isinstance(instance.function, wrapt.ObjectProxy))

    def test_staticmethod_type_inheritence(self):
        @wrapt.decorator
        def _decorator(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        class Class(object):
            @_decorator
            @staticmethod
            def function(*args, **kwargs):
                return args, kwargs

            self.assertTrue(isinstance(function, wrapt.FunctionWrapper))
            self.assertTrue(isinstance(function, wrapt.ObjectProxy))

        instance = Class()

        self.assertFalse(isinstance(instance.function, wrapt.FunctionWrapper))
        self.assertTrue(isinstance(instance.function, wrapt.ObjectProxy))

class TestAttributeAccess(unittest.TestCase):

    def test_function_attributes(self):
        def decorator1(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)
        decorator2 = wrapt.decorator(decorator1)

        def function1(*args, **kwargs):
            return args, kwargs
        function2 = decorator2(function1)

        self.assertEqual(function2.__wrapped__, function1)
        self.assertEqual(function2._self_wrapper, decorator1)
        self.assertEqual(function2._self_binding, 'instancemethod')

    def test_instancemethod_attributes(self):
        def decorator1(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)
        decorator2 = wrapt.decorator(decorator1)

        class Class(object):
            def function1(self, *args, **kwargs):
                return args, kwargs
            function2 = decorator2(function1)

            self.assertEqual(function2.__wrapped__, function1)
            self.assertEqual(function2._self_wrapper, decorator1)
            self.assertEqual(function2._self_binding, 'instancemethod')

        instance = Class()

        self.assertEqual(instance.function2.__wrapped__, instance.function1)
        self.assertEqual(instance.function2._self_instance, instance)
        self.assertEqual(instance.function2._self_wrapper, decorator1)

    def test_classmethod_attributes(self):
        def decorator1(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)
        decorator2 = wrapt.decorator(decorator1)

        class Class(object):
            @classmethod
            def function1(cls, *args, **kwargs):
                return args, kwargs
            function2 = decorator2(function1)

            self.assertEqual(function2.__wrapped__, function1)
            self.assertEqual(function2._self_wrapper, decorator1)
            self.assertEqual(function2._self_binding, 'classmethod')

        instance = Class()

        self.assertEqual(instance.function2.__wrapped__, instance.function1)
        self.assertEqual(instance.function2._self_instance, instance)
        self.assertEqual(instance.function2._self_wrapper, decorator1)

    def test_staticmethod_attributes(self):
        def decorator1(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)
        decorator2 = wrapt.decorator(decorator1)

        class Class(object):
            @staticmethod
            def function1(*args, **kwargs):
                return args, kwargs
            function2 = decorator2(function1)

            self.assertEqual(function2.__wrapped__, function1)
            self.assertEqual(function2._self_wrapper, decorator1)
            self.assertEqual(function2._self_binding, 'staticmethod')

        instance = Class()

        self.assertEqual(instance.function2.__wrapped__, instance.function1)
        self.assertEqual(instance.function2._self_instance, instance)
        self.assertEqual(instance.function2._self_wrapper, decorator1)

class TestParentReference(unittest.TestCase):

    def test_function_decorator(self):
        @wrapt.decorator
        def _decorator(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        @_decorator
        def function():
            pass

        self.assertEqual(function._self_parent, None)

    def test_class_decorator(self):
        @wrapt.decorator
        def _decorator(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        @_decorator
        class Class:
            pass

        self.assertEqual(Class._self_parent, None)

    def test_instancemethod(self):
        @wrapt.decorator
        def _decorator(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        class Class:
            @_decorator
            def function_im(self):
                pass

        c = Class()

        self.assertNotEqual(c.function_im._self_parent, None)
        self.assertNotEqual(Class.function_im._self_parent, None)

    def test_classmethod(self):
        @wrapt.decorator
        def _decorator(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        class Class:
            @_decorator
            @classmethod
            def function_cm(cls):
                pass

        self.assertNotEqual(Class.function_cm._self_parent, None)

    def test_staticmethod_inner(self):
        @wrapt.decorator
        def _decorator(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        class Class:
            @_decorator
            @staticmethod
            def function_sm_inner():
                pass

        self.assertNotEqual(Class.function_sm_inner._self_parent, None)

class TestGuardArgument(unittest.TestCase):

    def test_boolean_false_guard_on_decorator(self):
        @wrapt.decorator(enabled=False)
        def _decorator(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        @_decorator
        def function():
            pass

        self.assertFalse(isinstance(function, wrapt.FunctionWrapper))

    def test_boolean_true_guard_on_decorator(self):
        @wrapt.decorator(enabled=True)
        def _decorator(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        @_decorator
        def function():
            pass

        self.assertTrue(isinstance(function, wrapt.FunctionWrapper))

    def test_boolean_dynamic_guard_on_decorator(self):
        class Guard(object):
            value = True
            def __nonzero__(self):
                return self.value
            __bool__ = __nonzero__

        guard = Guard()

        result = []

        @wrapt.decorator(enabled=guard)
        def _decorator(wrapped, instance, args, kwargs):
            result.append(1)
            return wrapped(*args, **kwargs)

        @_decorator
        def function():
            pass

        self.assertTrue(isinstance(function, wrapt.FunctionWrapper))

        function()

        self.assertNotEqual(len(result), 0)

        result = []
        guard.value = False

        function()

        self.assertEqual(len(result), 0)

    def test_function_guard_on_decorator(self):
        value = True
        def guard():
            return value

        result = []

        @wrapt.decorator(enabled=guard)
        def _decorator(wrapped, instance, args, kwargs):
            result.append(1)
            return wrapped(*args, **kwargs)

        @_decorator
        def function():
            pass

        self.assertTrue(isinstance(function, wrapt.FunctionWrapper))

        function()

        self.assertNotEqual(len(result), 0)

        result = []
        value = False

        function()

        self.assertEqual(len(result), 0)

    def test_guard_on_instancemethod(self):
        value = True
        def guard():
            return value

        result = []

        @wrapt.decorator(enabled=guard)
        def _decorator(wrapped, instance, args, kwargs):
            result.append(1)
            return wrapped(*args, **kwargs)

        class Class(object):
            @_decorator
            def function(self):
                pass

        c = Class()

        self.assertTrue(isinstance(c.function, wrapt.BoundFunctionWrapper))

        c.function()

        self.assertNotEqual(len(result), 0)

        result = []
        value = False

        self.assertFalse(isinstance(c.function, wrapt.BoundFunctionWrapper))

        c.function()

        self.assertEqual(len(result), 0)

class TestDerivedFunctionWrapper(unittest.TestCase):

    def test_override_bound_type(self):

        class _BoundFunctionWrapper(wrapt.BoundFunctionWrapper):
            ATTRIBUTE = 1

        class _FunctionWrapper(wrapt.FunctionWrapper):
            __bound_function_wrapper__ = _BoundFunctionWrapper

        def function():
            pass

        def wrapper(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        _wrapper = _FunctionWrapper(function, wrapper)

        self.assertTrue(isinstance(_wrapper, _FunctionWrapper))

        instance = object()

        _bound_wrapper = _wrapper.__get__(instance, type(instance))

        self.assertTrue(isinstance(_bound_wrapper, _BoundFunctionWrapper))
        self.assertEqual(_bound_wrapper.ATTRIBUTE, 1)

class TestFunctionBinding(unittest.TestCase):

    def test_double_binding(self):

        def function():
            pass

        def wrapper(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        _wrapper = wrapt.FunctionWrapper(function, wrapper)

        self.assertTrue(isinstance(_wrapper, wrapt.FunctionWrapper))

        instance = object()

        _bound_wrapper_1 = _wrapper.__get__(instance, type(instance))

        self.assertTrue(isinstance(_bound_wrapper_1,
                wrapt.BoundFunctionWrapper))

        _bound_wrapper_2 = _bound_wrapper_1.__get__(instance, type(instance))

        self.assertTrue(isinstance(_bound_wrapper_2,
                wrapt.BoundFunctionWrapper))

        self.assertTrue(_bound_wrapper_1 is _bound_wrapper_2)

if __name__ == '__main__':
    unittest.main()

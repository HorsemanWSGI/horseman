from abc import ABC, abstractmethod
import horseman.path
from urllib.parse import unquote


class ResolveError(Exception):
    """Exception raised when a path resolution fails.
    """


class ModelLookup(ABC):
    """Looks up a model using consumers.
    """

    @abstractmethod
    def register(self, cls, consumer):
        """Registers a new consumer.
        """

    @abstractmethod
    def lookup(self, obj):
        """Iterator over all relevant consumers
        """

    def __call__(self, obj, stack):
        """Traverses following stack components and starting from obj.
        """
        unconsumed = stack.copy()
        while unconsumed:
            for consumer in self.lookup(obj):
                any_consumed, obj, unconsumed = consumer(obj, unconsumed)
                if any_consumed:
                    # Something was consumed, we exit.
                    break
            else:
                # nothing could be consumed
                return obj, unconsumed
        return obj, unconsumed


class ViewLookup(ABC):
    """Looks up a view using a given method.
    """

    @abstractmethod
    def lookup(self, obj, name, environ):
        """Resolves a view given an object and a name
        """

    def __call__(self, obj, stack, environ, default='index'):
        """Resolves a view.
        """
        default_fallback = False
        unconsumed_amount = len(stack)
        if unconsumed_amount == 0:
            default_fallback = True
            ns, name = horseman.path.Namespace.view, default
        elif unconsumed_amount == 1:
            ns, name = stack[0]
        else:
            raise ResolveError(
                "Can't resolve view: stack is not fully consumed.")

        if ns not in horseman.path.Namespace:
            raise ResolveError(
                "Can't resolve view: namespace %r is not supported." % ns)

        view = self.lookup(obj, name, environ)
        if view is None:
            if default_fallback:
                raise ResolveError(
                    "Can't resolve view: no default view on %r." % obj)
            else:
                if ns == horseman.path.Namespace.view.value:
                    raise ResolveError(
                        "Can't resolve view: no view `%s` on %r." % (
                            name, obj))
                raise ResolveError(
                    "%r is neither a view nor a model." % name)
        return view


class Publisher(ABC):
    """A publisher using model and view lookup components.
    """
    model_lookup: ModelLookup
    view_lookup: ViewLookup

    def publish(self, root, environ):
        path = unquote(
            environ['PATH_INFO'].encode('latin-1').decode('utf-8'))
        stack = horseman.path.parse_path(path)
        model, crumbs = self.model_lookup(root, stack)
        component = self.view_lookup(model, crumbs, environ)

        # The model needs an renderer
        if component is None:
            raise PublicationError('%r can not be rendered.' % model)

        return component

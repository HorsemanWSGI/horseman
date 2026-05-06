from functools import cached_property


class immutable_cached_property(cached_property):

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __delete__(self, instance):
        del instance.__dict__[self.attrname]

from frozendict import frozendict
from typing import (
    cast, Optional, Union, Any, Mapping, List, Iterable, Tuple, Dict)


Pairs = Iterable[Tuple[str, Any]]


class FormData(Dict[str, List[Any]]):

    def __init__(self, data: Optional[Union['FormData', Dict, Pairs]] = None):
        if data is not None:
            if isinstance(data, FormData):
                super().__init__(data)
            elif isinstance(data, Mapping):
                for key, value in data.items():
                    self.add(key, value)
            else:
                value = cast(Pairs, data)
                for key, value in value:
                    self.add(key, value)

    def get(self, name: str, default: Optional[Any] = None) -> Any:
        """Return the first value of the found list.
        """
        return super().get(name, [default])[0]

    def getlist(self, name: str, default: Optional[Any] = None) -> List[Any]:
        """Return the value list
        """
        return super().get(name, default)

    def pairs(self) -> Pairs:
        for key, values in self.items():
            for value in values:
                yield key, value

    def add(self, name: str, value: Any) -> None:
        if name in self:
            self[name].append(value)
        else:
            self[name] = [value]

    def to_dict(self, frozen=True):
        impl = frozendict if frozen else dict
        return impl(
            {k: (v[0] if len(v) == 1 else v) for k, v in self.items()}
        )


class TypeCastingDict(FormData):
    TRUE_STRINGS = {'t', 'true', 'yes', '1', 'on'}
    FALSE_STRINGS = {'f', 'false', 'no', '0', 'off'}
    NONE_STRINGS = {'n', 'none', 'null'}

    def bool(self, key: str, default=...):
        value = self.get(key, default)
        if value in (True, False, None):
            return value
        value = value.lower()
        if value in self.TRUE_STRINGS:
            return True
        elif value in self.FALSE_STRINGS:
            return False
        elif value in self.NONE_STRINGS:
            return None
        raise ValueError(f"Can't cast {value!r} to boolean.")

    def int(self, key: str, default=...):
        return int(self.get(key, default))

    def float(self, key: str, default=...):
        return float(self.get(key, default))

from horseman.http import Multidict


class TestMultidict:

    def test_empty(self):
        multidict = Multidict()
        assert multidict == {}
        assert isinstance(multidict, dict)

    def test_init_with_value(self):
        multidict = Multidict({'a': 1, 'foo': 'bar'})
        assert multidict == {'a': 1, 'foo': 'bar'}
        assert isinstance(multidict, dict)

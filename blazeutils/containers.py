import six

class LazyDict(dict):
    def __init__(self, *args, **kwargs):
        self._ld_initialized = kwargs.pop('_ld_initialize', True)
        dict.__init__(self, *args, **kwargs)

    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        raise AttributeError("'%s' object has no attribute '%s'"
            % (self.__class__.__name__, attr))

    def __setattr__(self, item, value):
        # this test allows attributes to be set in the __init__ method
        if self.__dict__.has_key('_ld_initialized') == False or self.__dict__['_ld_initialized'] == False:
            self.__dict__[item] = value
        # any normal attributes are handled normally when they already exist
        # this would happen if they are given different values after initilization
        elif self.__dict__.has_key(item):
            self.__dict__[item] = value
        # if there is a property, then set use it
        elif self.__class__.__dict__.has_key(item) and isinstance(self.__class__.__dict__[item], property):
            self.__class__.__dict__[item].__set__(self, value)
        # attributes added after initialization are stored in _data
        else:
            self[item] = value

    def __delattr__(self, name):
        del self[name]

class _Attribute(six.text_type):
    def __add__(self, other):
        return _Attribute(u'{0} {1}'.format(self, other).lstrip(u' '))

class HTMLAttributes(LazyDict):
    def __init__(self, *args, **kwargs):
        LazyDict.__init__(self, *args, **kwargs)
        self._clean_keys()

    def __getattr__(self, attr):
        attr = self._clean_key(attr)
        if attr not in self:
            self[attr] = _Attribute()
        return self[attr]

    def __getitem__(self, key):
        key = self._clean_key(key)
        if key not in self:
            self[key] = _Attribute()
        return LazyDict.__getitem__(self, key)

    def __setattr__(self, item, value):
        item = self._clean_key(item)
        value = _Attribute(value)
        LazyDict.__setattr__(self, item, value)

    def __setitem__(self, key, value):
        key = self._clean_key(key)
        value = _Attribute(value)
        LazyDict.__setitem__(self, key, value)

    def _clean_key(self, key):
        if key.endswith('_'):
            key = key[:-1]
        return key

    def _clean_keys(self):
        for key in self.keys():
            new_key = self._clean_key(key)
            if new_key != key:
                # have to use LazyDict b/c our __getitem__ will clean `key` and
                # give us an empty value because the cleaned key obviously
                # does not exist ye
                value = LazyDict.__getitem__(self, key)
                self[new_key] = value
                del self[key]

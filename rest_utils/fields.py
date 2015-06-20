__author__ = 'faddey'


class ClassField(models.CharField):

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.is_new_style = kwargs.pop('new_style', True)
        self.expected_super_class = kwargs.pop('super_class', object)
        kwargs.setdefault('max_length', 250)
        super(ClassField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if self._check_class(value):
            return self.get_prep_value(value)  # WTF??? this makes field working with loaddata command
        if not isinstance(value, basestring):
            raise ValidationError("WTF?")
        class_path = value.split('.')
        assert len(class_path) >= 0  # path to class must have a dot
        class_name = class_path[-1]
        module = __import__('.'.join(class_path[:-1]))
        for sub_mod_name in class_path[1:-1]:
            module = getattr(module, sub_mod_name)
        cls = getattr(module, class_name)
        if not self._check_class(cls):
            raise ValidationError("Our DB storing incorrect class reference")
        return cls

    def _check_class(self, cls):
        if not isclass(cls):
            return False
        if self.is_new_style:
            if not issubclass(cls, self.expected_super_class):
                return False
        return True

    def get_prep_value(self, value):
        if self._check_class(value):
            return value.__module__ + '.' + value.__name__
        if isinstance(value, basestring):
            return value
        return None
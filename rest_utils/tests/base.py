import traceback

__author__ = 'faddey'


class AssertNotRaisesMixin(object):

    def assertNotRaises(self, callable_obj, *args, **kwargs):
        try:
            callable_obj(*args, **kwargs)
        except:
            msg = ("Function raises an exception unexpectedly\n"
                   "Original exception was:\n\n" + traceback.format_exc())
            self.fail(msg)
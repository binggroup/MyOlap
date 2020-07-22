# -*- coding: utf-8 -*-



class _const:
    class ConstError(TypeError): pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("Can't rebind const (%s)" % name)
        self.__dict__[name] = value


# import sys
# sys.modules[__name__] = _const()

_const.COLUMN_TYPE_DIM = 0     #维度
_const.COLUMN_TYPE_METRIC = 2  #度量

_const.SQL_FIELD_TYPE_STR ='字符串'
_const.SQL_FIELD_TYPE_DATE ='日期'
_const.SQL_FIELD_TYPE_NUM ='数值'
#include "parser.h"

PyObject *replace(PyObject *text, PyObject *dict)
{
    PyObject *key, *value;
    Py_ssize_t pos = 0;

    while (PyDict_Next(dict, &pos, &key, &value))
    {
        text = PyUnicode_Replace(text, key, value, -1);
    }
    return text;
}

PyObject *decode(char *s, PyObject *extra, PyObject *trans)
{
    size_t len = strlen(s);
    PyObject *str = PyUnicode_Decode(s, len, codec, "replace");
    str = replace(str, extra);
    str = replace(str, trans);
    return str;
}

char *encode(PyObject *unicode, PyObject *extra, PyObject *trans)
{
    PyObject *str = unicode;
    str = replace(str, trans);
    str = replace(str, extra);
    PyObject *buf = PyUnicode_AsEncodedString(str, codec, "replace");
    return PyBytes_AsString(buf);
}
#include <Python.h>

static PyObject *method_pad(PyObject *self, PyObject *args)
{
    char *input_path, *output_path = NULL;
    long int start_byte, stop_byte;
    int len = 0;
    int max_len = 0;
    int nb_bytes_read = 0;

    char line[1000];
    char format[10];

    /* Parse arguments */
    if (!PyArg_ParseTuple(args, "ssll", &input_path, &output_path, &start_byte, &stop_byte))
    {
        return NULL;
    }

    long int amplitude = stop_byte - start_byte;

    /* Open and test the input file */
    FILE *input_fptr = fopen(input_path, "r");
    FILE *output_fptr = fopen(output_path, "w");

    /* Get file max length */
    fseek(input_fptr, start_byte, SEEK_SET);

    while (nb_bytes_read < amplitude)
    {
        fgets(line, sizeof(line), input_fptr);
        len = strlen(line);
        max_len = len > max_len ? len : max_len;
        nb_bytes_read += len;
    }

    nb_bytes_read = 0;

    /* Pad */
    fseek(input_fptr, start_byte, SEEK_SET);
    sprintf(format, "%%-%ds\n", max_len - 1);

    while (nb_bytes_read < amplitude)
    {
        fgets(line, sizeof(line), input_fptr);
        len = strlen(line);
        line[strlen(line) - 1] = '\0';
        fprintf(output_fptr, format, line);
        nb_bytes_read += len;
    }

    fclose(output_fptr);
    fclose(input_fptr);

    return PyLong_FromLong(0);
}

static PyMethodDef FpadAndSampleMethods[] = {
    {"pad", method_pad, METH_VARARGS, "Fast pad"},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef fast_pad_and_sample_module = {
    PyModuleDef_HEAD_INIT,
    "fast_pad_and_sample",
    "Fast pad and sample",
    -1,
    FpadAndSampleMethods};

PyMODINIT_FUNC
PyInit_fast_pad_and_sample(void)
{
    return PyModule_Create(&fast_pad_and_sample_module);
}
#include <Python.h>
#include <math.h>

typedef struct
{
    float min;
    float max;
} min_max;

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
    if (!PyArg_ParseTuple(
            args, "ssll", &input_path, &output_path, &start_byte, &stop_byte))
        return NULL;

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

static PyObject *method_sample(PyObject *self, PyObject *args)
{
    char *input_path, *output_path = NULL;
    long int x_index, nb_values, period, start_byte, stop_byte;
    PyObject *py_deltas;

    /* Parse arguments */
    if (!PyArg_ParseTuple(args,
                          "sslOllll",
                          &input_path,
                          &output_path,
                          &x_index,
                          &py_deltas,
                          &nb_values,
                          &period,
                          &start_byte,
                          &stop_byte))
        return NULL;

    Py_ssize_t deltas_len = PyList_Size(py_deltas);
    long *deltas = (long *)calloc(deltas_len, sizeof(long));

    for (int i = 0; i < deltas_len; i++)
    {
        PyObject *delta = PyList_GetItem(py_deltas, i);

        if (!PyLong_Check(delta))
            return NULL;

        deltas[i] = PyLong_AsLong(delta);
    }

    min_max *min_max_tuples = (min_max *)calloc(nb_values, sizeof(min_max));

    for (int i = 0; i < nb_values; i++)
    {
        min_max_tuples[i].min = INFINITY;
        min_max_tuples[i].max = -INFINITY;
    }

    long line_num = 0;
    long nb_bytes_read = 0;
    long amplitude = stop_byte - start_byte;

    char line[1000];
    char x_value[50];

    FILE *input_fptr = fopen(input_path, "r");
    FILE *output_fptr = fopen(output_path, "a");

    fseek(input_fptr, start_byte, SEEK_SET);

    while (nb_bytes_read < amplitude)
    {
        fgets(line, sizeof(line), input_fptr);
        long len = (long)strlen(line);
        char *value_string = strtok(line, ",");

        for (int i = 0; i < deltas_len; i++)
        {
            int delta = deltas[i];

            for (int j = 0; j < delta; j++)
                value_string = strtok(NULL, ",");

            if (i != x_index)
            {
                float value = atof(value_string);
                float current_min_value = min_max_tuples[i].min;
                float current_max_value = min_max_tuples[i].max;

                min_max_tuples[i].min = value < current_min_value ? value : current_min_value;
                min_max_tuples[i].max = value > current_max_value ? value : current_min_value;
            }
            else if (line_num % period == 0)
                strcpy(x_value, value_string);
        }

        if (line_num % period == period - 1)
        {
            fprintf(output_fptr, "%s,", x_value);

            for (int i = 0; i < nb_values - 1; i++)
                if (i != x_index)
                    fprintf(output_fptr, "%f,%f,", min_max_tuples[i].min, min_max_tuples[i].max);

            fprintf(output_fptr, "%f,%f\n",
                    min_max_tuples[nb_values - 1].min,
                    min_max_tuples[nb_values - 1].max);

            for (int i = 0; i < nb_values; i++)
            {
                min_max_tuples[i].min = INFINITY;
                min_max_tuples[i].max = -INFINITY;
            }
        }

        line_num++;
        nb_bytes_read += len;
    }

    if ((line_num - 1) % period != period - 1)
    {
        fprintf(output_fptr, "%s,", x_value);

        for (int i = 0; i < nb_values - 1; i++)
            if (i != x_index)
                fprintf(output_fptr, "%f,%f,", min_max_tuples[i].min, min_max_tuples[i].max);

        fprintf(output_fptr, "%f,%f\n",
                min_max_tuples[nb_values - 1].min,
                min_max_tuples[nb_values - 1].max);
    }

    fclose(output_fptr);
    fclose(input_fptr);

    free(min_max_tuples);
    free(deltas);
    return PyLong_FromLong(0);
}

static PyObject *method_sample_sampled(PyObject *self, PyObject *args)
{
    const char *input_path;
    const char *output_path;
    long int nb_y_values, period;
    long int line_num = 0;
    int has_header;

    char line[1000];
    char x_value[50];

    /* Parse arguments */
    if (!PyArg_ParseTuple(args,
                          //   "ssll",
                          "ssllp",
                          &input_path,
                          &output_path,
                          &nb_y_values,
                          &period,
                          &has_header))
        return NULL;

    FILE *input_fptr = fopen(input_path, "r");
    FILE *output_fptr = fopen(output_path, "a");

    if (has_header)
    {
        fgets(line, sizeof(line), input_fptr);
    }

    float *values = (float *)calloc(nb_y_values, sizeof(float));

    for (int i = 0; i < nb_y_values; i++)
        values[i] = i % 2 == 0 ? INFINITY : -INFINITY;

    while (fgets(line, sizeof(line), input_fptr))
    {
        char *value_string = strtok(line, ",");

        if (line_num % period == 0)
            strcpy(x_value, value_string);

        for (int i = 0; i < nb_y_values; i++)
        {
            value_string = strtok(NULL, ",");
            float value = atof(value_string);
            float current_value = values[i];

            values[i] = i % 2 == 0 ? (value < current_value ? value : current_value)
                                   : (value > current_value ? value : current_value);
        }

        if (line_num % period == period - 1)
        {
            fprintf(output_fptr, "%s,", x_value);

            for (int i = 0; i < nb_y_values - 1; i++)
                fprintf(output_fptr, "%f,", values[i]);

            fprintf(output_fptr, "%f\n", values[nb_y_values - 1]);

            for (int i = 0; i < nb_y_values; i++)
                values[i] = i % 2 == 0 ? INFINITY : -INFINITY;
        }

        line_num++;
    }

    if ((line_num - 1) % period != period - 1)
    {
        fprintf(output_fptr, "%s,", x_value);

        for (int i = 0; i < nb_y_values - 1; i++)
            fprintf(output_fptr, "%f,", values[i]);

        fprintf(output_fptr, "%f\n", values[nb_y_values - 1]);
    }

    fclose(output_fptr);
    fclose(input_fptr);
    free(values);

    return PyLong_FromLong(0);
}

static PyMethodDef FpadAndSampleMethods[] = {
    {"pad", method_pad, METH_VARARGS, "Fast pad"},
    {"sample", method_sample, METH_VARARGS, "Fast sample"},
    {"sample_sampled", method_sample_sampled, METH_VARARGS, "Fast sample sampled"},
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
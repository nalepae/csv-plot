<div align="center">
  <img src="https://github.com/nalepae/csv-plot/blob/master/csv_plot/assets/icon-256.png"><br>
</div>

----------------
# CSV Plot: easy and powerful plotting tool for CSV files

## What is it?
**CSV Plot** is a tool to easily plot any CSV file, of any size, without never getting out of memory errors.
(Only data which is displayed on the screen is loaded into memory.)

It works with user friendly YAML configuration files, to let you choose the layout, colors, units, legends...

**CSV Plot** is built on top of the amazing [PyQtGraph](https://www.pyqtgraph.org/) library, which ensures a nice and smooth experience, as plotting should always be.

## Installation
```
$ pip install csv-plot
```

## Usage
```
$ csv-plot <path to CSV file> -c <path to configuration file>
```

- To move: Hold mouse left button
- To zoom:
  - Use mouse scroll wheel, or
  - Hold mouse right button

With this [CSV file](https://github.com/nalepae/csv-plot/blob/master/docs/example_file.csv):
```
index,sin,cos,sin_rand,cos_rand
0,0,1,-0.07456652762,1.039341379
1,0.06379051953,0.9990267284,0.122423516,1.098801076
2,0.1273332336,0.9941147013,0.1391795401,0.9790017212
3,0.1903813146,0.9852872507,0.2364198969,0.8756242061
4,0.2526898872,0.9725831611,0.3508306833,0.9489513789
5,0.3140169944,0.9560565163,0.3985702648,1.018873161
6,0.3741245527,0.9357764859,0.4404979239,0.8948342146
7,0.4327792916,0.9118270525,0.4145093978,0.9751999311
8,0.4897536741,0.88430668,0.4701196006,1.004694956
9,0.544826795,0.8533279255,0.5498124736,0.8812543224
...
```
and this [configuration file](https://github.com/nalepae/csv-plot/blob/master/docs/example_configuration.yaml):
```YAML
general:
  variable: index # Mandatory - The column in CSV file corresponding to X axis
  label: Time # Optional      - Label of horizontal axis
  unit: sec # Optional        - Unit of horizontal axis

layout:
  - position: 1-1 # Mandatory - `Raw number`-`Column number` of the plot widget
    title: Waves # Optional   - Title of the (1-1) plot widget
    label: Height # Optional  - Label of vertical axis for the (1-1) plot widget
    unit: m # Optional        - Unit of vertical axis for the (1-1) plot widget

  - position: 2-1
    title: Waves with some randomness
    label: Height
    unit: m

curves:
  - position: 1-1 # Mandatory - `Raw number`-`Column number`
    variable: sin # Mandatory - The column in CSV file corresponding to Y axis

  - position: 1-1
    variable: cos
    color: green # Optional - Curve color - Default to yellow

  - position: 2-1
    variable: sin_rand
    color: purple

  - position: 2-1
    variable: cos_rand
    color: aqua
```

We get this result:
<div align="center">
  <img src="https://github.com/nalepae/csv-plot/blob/master/docs/example.png"><br>
</div>

## Special notice
The column corresponding to the X axis MUST be sorted. In the contrary, the behavior is unpredictable.

## DateTime as X axis
If your CSV time presents a dateTime as X axis, like in the following example with the `time` column:
```
time,trade_id,price,side,size
2019-08-15 16:03:06.595+00,1,0.7597,sell,500.0
2019-08-15 16:03:06.595+00,2,0.7599,sell,1000.0
2019-08-15 16:03:06.595+00,3,0.76,sell,1000.0
2019-08-15 16:03:06.595+00,4,0.7601,sell,1000.0
2019-08-15 16:03:06.595+00,5,0.7602,sell,1000.0
2019-08-15 16:03:18.894+00,6,0.7597,sell,500.0
2019-08-15 16:03:18.894+00,7,0.7599,sell,1000.0
2019-08-15 16:03:21.279+00,8,0.76,buy,385.0
2019-08-15 16:03:21.554+00,9,0.76,buy,500.0
2019-08-15 16:03:23+00,10,0.76,buy,500.0
2019-08-15 16:03:23.75+00,11,0.76,buy,476.0
2019-08-15 16:03:23.91+00,12,0.76,buy,1000.0
2019-08-15 16:03:23.913+00,13,0.76,buy,1000.0
```
then a `dateTimeFormat` has to be added into the `general` section, like:
```YAML
general:
  variable: time
  dateTimeFormat:
  - "%Y-%m-%d %H:%M:%S.%f+00"
```

The string `"%Y-%m-%d %H:%M:%S.%f+00"` correspond to the [strptime](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior) format argument.
If, in the same CSV file, multiple dateTime formats are provided, you can specify all of them in the `dateTimeFormat` list, like:
```YAML
general:
  variable: time
  dateTimeFormat:
  - "%Y-%m-%d %H:%M:%S.%f+00"
  - "%Y-%m-%d %H:%M:%S+00"
```

Keep in mind that for each line of the CSV file, **CSV Plot** will evaluate the dateTime string against each of `dateTimeFormat` value,
and will stop to the first one which is successful. So write first the format which is the most likely to happen in the CSV file.


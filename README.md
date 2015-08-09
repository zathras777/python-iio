# python-iio

## How

```
$ python-iio --show-devices
Dev Sensor          Channel                                  Enabled? Index Format
--- --------------  ---------------------------------------  -------- ----- ------
 0  magn_3d         in_magn_x                                False    0     le:s32/32>>0
                    in_magn_y                                False    1     le:s32/32>>0
                    in_magn_z                                False    2     le:s32/32>>0
                    in_rot_from_north_magnetic_tilt_comp     False    3     le:s16/32>>0
 1  incli_3d        in_incli_x                               False    0     le:s16/32>>0
                    in_incli_y                               False    1     le:s16/32>>0
                    in_incli_z                               False    2     le:s16/32>>0
 2  als             in_intensity_both                        False    0     le:s32/32>>0
 3  dev_rotation    in_rot_quaternion                        False    0     le:s32/32X4>>0
 4  gyro_3d         in_anglvel_x                             False    0     le:s32/32>>0
                    in_anglvel_y                             False    1     le:s32/32>>0
                    in_anglvel_z                             False    2     le:s32/32>>0
 5  accel_3d        in_accel_x                               False    0     le:s16/32>>0
                    in_accel_y                               False    1     le:s16/32>>0
                    in_accel_z                               False    2     le:s16/32>>0
```

## What
A module to access linux IIO devices and their data.

## Why?
This is mainly a proof of concept to see what data can be used and how to interpret it. Hopefuly it will prove useful to others.

## Framework
The IIO framework works well for getting the values, but it's not always clear what the values mean or how they should be used. This probably shows my lack of experience with such low level sensors, but I haven't managed to find any decent resources to explain this either, so maybe it's a more general lack of help?

## Returned Values
- in_incli_x|y|z appear to be radians giving the inclination of the screen, but where exactly the origins are is still not 100% clear for all axes.
- the first 2 values from als aren't valid, so you need to read at least 3 before you have a usable value. Not sure if this can be fixed by better sensor support?
- dev_rotation returns quaternion values, so creating a usable vector would be useful.

## ToDo
- add python 3 support
- actually do something useful with the returned values.


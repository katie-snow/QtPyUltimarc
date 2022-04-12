# Ultimarc Command Line Tools

The Ultimarc command line tools can be used to program different Ultimarc USB devices attached 
to the local machine. The command line tools are launched through an integrated launcher command.
Addtionally Bash autocompletion can be enabled by sourcing the `tools.bash` file in your .bashrc profile.

&nbsp; 

### Device Matching And Filtering
If the `--bus` and `--address` arguments are not specified, device configuration changes will be applied 
to all devices discovered by the tool.  If only the `--bus` argument is specifed, all devices on that 
bus will be matched.  To target a specific device, the `--bus` and `--address` arguments must be specified.

&nbsp; 

### Running the tool

If you have installed the Ultimarc Python package use this command line to run the tools:

```ultimarc-cli [TOOL NAME]```

If you are running tools from a copy of the GitHub project use this command line from the `ultimarc` 
directory:

```python3 -m tools [TOOL NAME] ```

To get a list of available tools to run:

```ultimarc-cli --help``` or ```python3 -m tools --help```

To get help for a specific tool run:

```ultimarc-cli [TOOL NAME] --help```

&nbsp; 

### Common Tool Arguments

These are the common tool command line arguments.  These options are available for every tool.

#### Help

You can show help for the launcher or each tool by adding the help argument.  No other arguments 
are allowed when using the help argument.

```-h, --help```

#### Debug

Debugging output can be enabled if the debug argument is added.  The debugging argument can be 
used with any other tool argument.

```--debug```

#### Log File Output

All output can be written to a log file.  The log file argument can be used with any other argument.
You may need to wrap the filename value with double quotes if there are spaces in the path or filename.
The log file is written out to the current directory and will have a `[TOOL].log` suffix.

```--log-file```

#### Quiet Output

All output can be suppressed by using the quiet argument. The quiet argument can be used with any other 
argument.  

```-q, --quiet```

#### Bus Filter

The Bus filter will tell the tools to search for devices that have specified bus ID.

```--bus [BUS]```

#### Address Filter

The Address filter specifics a specific device ID on a bus. The `--bus` argument must also be set.

```--address [ADDRESS]```

&nbsp; 

### USB Button Tool

A tool for managing Ultimarc USB Button devices.

#### Tool Command Name

```usb-button```

#### --help

```
usage: usb-button [-h] [--debug] [--log-file] [-q] [--bus BUS] [--address ADDRESS] [--set-color INT,INT,INT]
                  [--set-random-color] [--get-color] [--set-config CONFIG-FILE]

manage usb-button devices.

optional arguments:
  -h, --help            show this help message and exit
  --debug               enable debug output
  --log-file            write output to a log file
  -q, --quiet           suppress normal output
  --bus BUS             filter by usb device bus number
  --address ADDRESS     filter by usb device address number
  --set-color INT,INT,INT
                        set usb button color with RGB value
  --set-random-color    randomly set usb button color
  --get-color           output current usb button color RGB value
  --set-config CONFIG-FILE
                        Set button config from config file.
```

#### --set-color

Configure a device with a specific color RGB color.  The values must be a comma delimited list 
of 3 integer values between 0 and 255.

Valid argument values are:
```
"123,123,123"
"RGB(123,123,123)"
```

#### --set-random-color

Configure the UP button position color with a randomly chosen RGB color.

#### --get-color

Return the currently configured RGB color value for the button UP position.  

Note: Currently returns `RGB(0,0,0)` for devices that have not yet been configured since being 
plugged in.

#### --set-config

Configure a device using the specified configuration file.  See `examples` directory for an 
example USB Button configuration JSON file.
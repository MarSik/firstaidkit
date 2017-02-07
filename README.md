# First Aid Kit

> Note this tool was written for very old Fedora versions and is not useful anymore. I am publishing it again just so it might be resurrected in the future (we see renewed interest in diagnostic and recovery tools).


A tool that automates simple and common recovery tasks.

For more information on how to use this application or on how
to develop plugins, refer to the documentation contained in
this package's documentation directory.

## Dependencies

The tool requires Python 2.x and bindings for GTK2 if GUI is requested. I will fallback to text mode when the bindings are not available.

## Building

No real build is necessary, but you can execute `make` to regenerate the version files.

## How to run

The basic GUI invocation looks like this

```
./firstaidkit -a -g gtk
```

## Screenshots

![Main screen](/doc/images/fak-main.png?raw=true "Main screen")
![Result screen](/doc/images/fak-results.png?raw=true "Results")
![Expert mode screen](/doc/images/fak-expert.png?raw=true "Expert mode")
![Flag editing](/doc/images/fak-flags.png?raw=true "Flag editing")
![Remode mode](/doc/images/fak-full.png?raw=true "Remote mode")


Three commands for the weigh scale:

 

c9.zero_scale()     # do this initially before taking readings.  Ensure nothing is on the scale before you zero it.

 

c9.read_scale()    # to take a single reading of the scale

 

c9.clear_scale()   # to clear the reading on the scale

 

c9.ready_steady_scale(True)   # waits till the scale acquires a steady reading before it returns the reading + True.  Until that happens, it keeps on returning the reading + False.

If you want to see the output, use a print statement around any of the above:

print(c9.read_scale())


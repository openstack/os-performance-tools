=====
Usage
=====

.. _counters:

os-collect-counters
-------------------

This is a command line program which will try to collect data from
various backends as rapidly as possible and then save a representation
of these as JSON. It can optionall wrap this JSON in subunit, which is
useful for appending to a subunit stream from previous tests.

os_performance_tools.counters2statsd
------------------------------------

This module is useful in a subunit processing stream for saving the
counters into statsd. It should be added as a target before processing
the stream, and then upon reaching the end, it will send the counters into
statsd. Currently this is limited to an attachment named 'counters.json'
but other schemes may be implemented in the future.

Please see counters_ for information on the backends and counters that
are supported.

This is a project I started as a result of getting an assignment from http://infobip.com (Described in doc/assignment.txt) as part of the interview.

As I mentioned, the assignment in its present format may be considered fulfilled. Any additional requirements could be satisfied, but first require to be specified explicitly.

Please keep in mind, that the toolkit should be tested by a skilled technical professional and is not intended as a direct turnkey "Plug-and-play" product (see below).

The monitoring should be pluggable to any commercial or free agent out there (Zabix/Nagios/Zenos or even HP OpenView for one).
The scripts could also be plugged into some web front-end with a configuration storage backend other then a text config file (i.e., some SQL or ZooKeeper), but I didn't do that intentionally, as this wasn't specified in the requirements, besides, this would be a bespoke commercial product then.

Overall, this is a good set of building blocks for almost any such system. A production-ready implementation could be then built in little to no time, should a specific set of requirements (or at least the target environment) be exhaustively specified.

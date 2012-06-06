python-libdeje
==============

_DEJE, n., Democratically Enforced JSON Environment._

DEJE is an EJTP protocol for tightly managed, verified, and timelined JSON
data. You can use it for any distributed data system that needs strong safety
guarantees.

DEJE includes Lua-based verification functions that run in a hardened Lua
environment ([hardlupa](https://github.com/campadrenalin/HardLupa)) and for
this reason, the library is highly portable to other languages. If it can run
a Lua runtime, and talk to the network, you can build a DEJE lib in that
language. This means platform compatibility across language and OS lines.

The first project that will be built with this as a dependency will be djdns,
a distributed DNS system that hosts a virtual DNS server on localhost based on
data in a set of heirarchical community-managed DNS documents.

Dependencies
============

 * Python >= 2.6.x
 * [HardLupa](https://github.com/campadrenalin/HardLupa)
 * [python-libejtp](https://github.com/campadrenalin/EJTP-lib-python)

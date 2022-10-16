Modules
=======

While different modules perform different tasks, their interfaces all follow
the same pattern as much as possible. For instance, all Hypercore action modules
do not support ``check_mode``, most of them can have their state set to either
``present`` or ``absent``, and they identify the resource to operate by using
the *name* (or equivalent) parameter.

The API of each module is composed of two parts. The *cluster_instance* parameter contains
the pieces of information that are related to the Hypercore backend that the
module is connecting to. All other parameters hold the information related to
the resource that we are operating on.


Authentication parameters
-------------------------

Descrcription about instance parameter.

Module reference
----------------

.. toctree::
   :glob:
   :maxdepth: 1

   modules/*

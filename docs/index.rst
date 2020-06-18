.. inmymind documentation master file, created by
   sphinx-quickstart on Thu Jun  4 17:30:41 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

inmymind's documentation
====================================

Welcome to my **inmymind** platform.

This is a review of the functionalists of the platform.
The main goal is to explain how can one extend the system,
and is free to choose the frameworks and the protocols he prefers.
This can be done by writing simple functions or classes,
and just dropping them to the subpackges as will be described.

The platform is very simple, it is all about choosing the **right names** for your functions,
and the magic will happen without any other effort.

The power of the platform is the **urls**. Give the platform the urls that match the desired
protocol and schemes, and you are ready to roll.


**Client**:

client:
   .. automodule:: inmymind.client.client
      :members:

Driver:
   .. automodule:: inmymind.client.drivers.basic_drivers
      :members:

Reader:
   .. automodule:: inmymind.client.readers.basic_readers
      :members:

Writer:
   .. automodule:: inmymind.client.writers.basic_writers
      :members:

.. toctree::
   :maxdepth: 2
   :caption: Contents:





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

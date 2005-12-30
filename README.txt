======
README
======

:Author: Marc-Aurèle DARCHE
:Revision: $Id$

.. sectnum::    :depth: 4
.. contents::   :depth: 4

The CPSI18n product contains scripts for making and updating CPS products
translations. This product also contains common translations shared by all CPS
products.

When you run udpate_pos be sure that your current locale is latin9 aware
otherwise some GNU gettext commands might not work.

For example do something like::

  $ export LC_ALL=fr_FR@euro


.. Local Variables:
.. mode: rst
.. End:
.. vim: set filetype=rst:

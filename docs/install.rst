.. include:: .special.rst

Installing
#####################################################

Install using docker
=====================================================

This is the recommended method as it will keep the bot self-contained, and will handle always re-starting the bot.

.. todo::
   fill this out

Now you can :ref:`Configure using docker`.

Install using pipenv
=====================================================

Using `pipenv <https://github.com/pypa/pipenv>`_ allows you to install this into a virtual environment.

Make sure you install pipenv first:

.. code-block:: console

   $ pip install --upgrade pipenv

Then use pipenv to create a virtual environment and install the package into it:

.. code-block:: console

   $ mkdir axonbot_slack
   $ cd axonbot_slack
   $ pipenv install axonbot-slack

Now you can :ref:`Configure using pipenv`.

Install using pip
=====================================================

Using `pip <https://pypi.org/project/pip/>`_ allows you to install this into the system wide packages.

.. code-block:: console

   $ pip install axonbot_slack

Now you can :ref:`Configure using pip`.

Install using github
=====================================================

.. code-block:: console

   $ git clone git@github.com:Axonius/axonbot_slack.git

Now you can :ref:`Configure using github`.

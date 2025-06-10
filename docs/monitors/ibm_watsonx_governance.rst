============================================
IBM watsonx.governance
============================================

In order to use ``IBM watsonx.governance`` you need to install the ``ibm-aigov-facts-client``, ``ibm-watson-openscale`` and ``ibm-watsonx-ai`` package.

.. code-block:: bash

    pip install ibm-aigov-facts-client ibm-watson-openscale ibm-watsonx-ai


Monitors
---------------------

.. autoclass:: pineflow.monitors.watsonx.WatsonxPromptMonitor
    :members:

.. autoclass:: pineflow.monitors.watsonx.WatsonxExternalPromptMonitor
    :members:

Custom Metrics
---------------------

.. autoclass:: pineflow.monitors.watsonx.WatsonxCustomMetric
    :members:

Credentials
---------------------

.. autoclass:: pineflow.monitors.watsonx.CloudPakforDataCredentials
    :members:

.. autoclass:: pineflow.monitors.watsonx.IntegratedSystemCredentials
    :members:

Supporting Classes
---------------------

.. autoclass:: pineflow.monitors.watsonx.WatsonxMetric
    :members:

.. autoclass:: pineflow.monitors.watsonx.WatsonxLocalMetric
    :members:

.. autoclass:: pineflow.monitors.watsonx.WatsonxMetricThreshold
    :members:
    
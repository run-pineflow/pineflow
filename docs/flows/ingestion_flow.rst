Ingestion Flow
============================================

.. autoclass:: pineflow.core.flows.IngestionFlow
   :members:

Enums
----------------

DocStrategy
________________

.. list-table::
   :header-rows: 1
   :widths: 20 50

   * - Name
     - Description
   * - DocStrategy.DUPLICATE_ONLY
     - Inserts only new, unique documents. Skips duplicates from the input batch and existing data in the vector store.
   * - DocStrategy.DUPLICATE_AND_DELETE
     - Deletes all existing documents in the vector store and replaces them with the new batch after removing duplicates.
   * - DocStrategy.DEDUPLICATE_OFF
     - Inserts all input documents as-is, regardless of duplicates or existing content.

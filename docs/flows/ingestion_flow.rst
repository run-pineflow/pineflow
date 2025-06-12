Ingestion Flow
============================================

.. autoclass:: pineflow.core.flows.IngestionFlow
   :members:

Enums
----------------

DedupStrategy
________________

.. list-table::
   :header-rows: 1
   :widths: 20 50

   * - Name
     - Description
   * - DedupStrategy.DUPLICATE_ONLY
     - Inserts only new, unique documents. Skips duplicates both from the input batch and existing data in the vector store.
   * - DedupStrategy.DUPLICATE_AND_DELETE
     - Deletes all existing documents in the vector store and replaces them with the new batch after removing duplicates.
   * - DedupStrategy.DEDUPLICATE_OFF
     - Inserts all input documents as-is, regardless of duplicates or existing content.

DedupStage
________________

.. list-table::
   :header-rows: 1
   :widths: 20 50

   * - Name
     - Description
   * - DedupStrategy.PRE_TRANSFORM
     - Deduplication happens before applying any transformations (e.g. chunking, embeddings).
   * - DedupStrategy.POST_TRANSFORM
     - Deduplication happens after the transformation step (e.g. after splitting documents).

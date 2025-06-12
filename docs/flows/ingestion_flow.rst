Ingestion Flow Documentation
=============================

Ingestion Flow
===============

.. autoclass:: pineflow.core.flows.IngestionFlow
   :exclude-members: run, __init__, __new__
   :undoc-members:
   :show-inheritance:

run()
~~~~~~

.. automethod:: pineflow.core.flows.IngestionFlow.run
   :noindex:

Deduplication Strategy
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 50 30

   * - Name
     - Description
     - When to Use
   * - duplicate_only
     - Inserts only new, unique documents. Skips duplicates both from the input batch and existing data in the vector store.
     - Use to safely add data without changing or deleting anything. Ensures uniqueness without loss.
   * - duplicate_and_delete
     - Deletes all existing documents in the vector store and replaces them with the new batch after removing duplicates.
     - Use when doing a full refresh or reindexing. Replaces the store content with only the clean, deduplicated batch.
   * - deduplicate_off
     - Inserts all input documents as-is, regardless of duplicates or existing content.
     - Use when you want raw ingestion or are relying on another system to manage duplication.

Deduplication Stage
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 50 30

   * - Name
     - Description
     - When to Use
   * - pre_transform
     - Deduplication happens before applying any transformations (e.g. chunking, embeddings).
     - Use to eliminate exact duplicates early and reduce unnecessary processing or transformation.
   * - post_transform
     - Deduplication happens after the transformation step (e.g. after splitting documents).
     - Use when deduplication should be based on the final transformed content (e.g. deduping chunks).

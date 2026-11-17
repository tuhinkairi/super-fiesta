
from context_aware_suggestion_rag.interfaces.vector_store import (
    VectorStore,
)
from context_aware_suggestion_rag.database.models import (
    DatabaseOperationResult,
    VectorQueryResult,
    VectorRecord,
)


class FakeVectorStore(VectorStore):

    def connect(self):
        pass

    def health_check(self):
        return True

    def upsert(self, records):
        return DatabaseOperationResult(
            success=True,
            operation="upsert",
            affected_count=len(records),
        )

    def query(
        self,
        vector,
        top_k=10,
        namespace="documents",
        filter=None,
        include_metadata=True,
        sparse_indices=None,
        sparse_values=None,
    ):
        return VectorQueryResult(
            matches=[],
            namespace=namespace,
        )

    def delete(self, ids, namespace="documents"):
        return DatabaseOperationResult(
            success=True,
            operation="delete",
            affected_count=len(ids),
        )

    def delete_namespace(self, namespace):
        return DatabaseOperationResult(
            success=True,
            operation="delete_namespace",
            affected_count=0,
        )

    def fetch(self, ids, namespace="documents"):
        return []

    def close(self):
        pass


def main():
    store = FakeVectorStore()

    assert isinstance(store, VectorStore)
    print("Vector store interface inheritance: PASS")

    store.connect()
    assert store.health_check()
    print("Connection and health check: PASS")

    record = VectorRecord(
        id="test-1",
        values=[0.1, 0.2, 0.3],
        namespace="documents",
    )

    upsert_result = store.upsert([record])
    assert upsert_result.success
    assert upsert_result.affected_count == 1
    print("Vector upsert interface: PASS")

    query_result = store.query(
        vector=[0.1, 0.2, 0.3],
        top_k=5,
    )

    assert isinstance(query_result, VectorQueryResult)
    print("Vector query interface: PASS")

    delete_result = store.delete(["test-1"])
    assert delete_result.success
    print("Vector deletion interface: PASS")

    namespace_result = store.delete_namespace("documents")
    assert namespace_result.success
    print("Namespace deletion interface: PASS")

    assert store.fetch(["test-1"]) == []
    print("Vector fetch interface: PASS")

    store.close()
    print("Connection close interface: PASS")

    print("\nAll vector store interface tests passed.")


if __name__ == "__main__":
    main()

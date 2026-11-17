
from neo4j import GraphDatabase
from graphrag_app.config import settings

print("Testing Neo4j AuraDB connection...")
print("URI:", settings.neo4j_uri)

driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(
        settings.neo4j_username,
        settings.neo4j_password,
    ),
)

try:
    driver.verify_connectivity()

    print("\nSUCCESS: AuraDB connection established!")

    with driver.session(database=settings.neo4j_database) as session:
        result = session.run(
            "RETURN 'AuraDB connection successful!' AS message"
        )
        print(result.single()["message"])

except Exception as error:
    print("\nCONNECTION FAILED")
    print("Exception type:", type(error).__name__)
    print("Error:", repr(error))
    print("Error code:", getattr(error, "code", None))

    cause = error.__cause__
    if cause:
        print("Underlying cause:", repr(cause))

finally:
    driver.close()

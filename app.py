from elasticsearch import Elasticsearch

# Try with SSL verification disabled
es = Elasticsearch(
    ["https://vs-production.es.ap-south-1.aws.elastic-cloud.com:9243"],
    basic_auth=("elastic", "yuBIlcwW4QIRAhAu8aboJUtW"),
    verify_certs=False
)

# Test the connection
print(f"Can connect: {es.ping()}")
if es.ping():
    print(f"Elasticsearch info: {es.info()}")
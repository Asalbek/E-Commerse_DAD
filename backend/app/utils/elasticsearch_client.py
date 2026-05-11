from elasticsearch import AsyncElasticsearch
from app.config import get_settings

settings = get_settings()

es_client = AsyncElasticsearch(
    hosts=[settings.ELASTICSEARCH_URL],
    request_timeout=30,
)

PRODUCT_INDEX = "products"

PRODUCT_INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "text", "analyzer": "standard", "fields": {
                "keyword": {"type": "keyword"},
                "autocomplete": {
                    "type": "text",
                    "analyzer": "autocomplete_analyzer",
                    "search_analyzer": "standard"
                }
            }},
            "description": {"type": "text", "analyzer": "standard"},
            "price": {"type": "float"},
            "stock_quantity": {"type": "integer"},
            "category": {"type": "keyword"},
            "category_id": {"type": "integer"},
            "sku": {"type": "keyword"},
            "image_url": {"type": "keyword"},
            "is_active": {"type": "boolean"},
            "created_at": {"type": "date"},
        }
    },
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "autocomplete_analyzer": {
                    "type": "custom",
                    "tokenizer": "autocomplete_tokenizer",
                    "filter": ["lowercase"]
                }
            },
            "tokenizer": {
                "autocomplete_tokenizer": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 15,
                    "token_chars": ["letter", "digit"]
                }
            }
        }
    }
}


async def create_product_index():
    """Create the products Elasticsearch index if it doesn't exist."""
    exists = await es_client.indices.exists(index=PRODUCT_INDEX)
    if not exists:
        await es_client.indices.create(index=PRODUCT_INDEX, body=PRODUCT_INDEX_MAPPING)


async def close_elasticsearch():
    await es_client.close()

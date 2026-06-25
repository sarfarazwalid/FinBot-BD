from app.ambiguity import is_ambiguous_banking_query, get_clarification_message, get_clarification_options
from app.llm.prompt_builder import detect_query_language

test_queries = [
    ("PIN kivabe reset korbo?", "banglish"),
    ("How to reset PIN?", "en"),
    ("How to reset bKash PIN?", "en"),
    ("Nagad PIN reset korbo kivabe?", "banglish"),
    ("What is the capital of France?", "en"),
    ("How to open account?", "en"),
    ("How to send money?", "en"),
    ("How to check balance?", "en"),
]

for query, expected_lang in test_queries:
    is_amb, intent = is_ambiguous_banking_query(query)
    lang = detect_query_language(query)
    print(f"Query: {query}")
    print(f"  Detected language: {lang} (expected: {expected_lang})")
    print(f"  Ambiguous: {is_amb}, Intent: {intent}")
    if is_amb and intent:
        print(f"  Clarification: {get_clarification_message(intent, lang)}")
        print(f"  Options: {get_clarification_options()}")
    print()
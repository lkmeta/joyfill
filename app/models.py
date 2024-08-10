from transformers import BertTokenizer, BertForMaskedLM
import torch
import re

# Load the BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertForMaskedLM.from_pretrained("bert-base-uncased")


def generate_bert_suggestions(masked_text: str, top_k: int = 10) -> list[str]:
    """
    Generate the top k suggestions for the [MASK] token in the input text using BERT.

    Args:
        masked_text (str): The input text with [MASK] in place of the word to predict.
        top_k (int): The number of top suggestions to return.

    Returns:
        list[str]: A list of the top_k suggestions.
    """
    # Tokenize the input text
    inputs = tokenizer(masked_text, return_tensors="pt")

    # Get the model's predictions
    with torch.no_grad():
        logits = model(**inputs).logits

    # Retrieve the index of [MASK]
    mask_token_index = (inputs.input_ids == tokenizer.mask_token_id)[0].nonzero(
        as_tuple=True
    )[0]

    # Get the top_k predicted tokens
    predicted_token_ids = (
        logits[0, mask_token_index].topk(top_k, dim=1).indices[0].tolist()
    )

    # Decode the predicted tokens into words and filter out non-alphanumeric tokens
    suggestions = [
        tokenizer.decode(token_id).strip() for token_id in predicted_token_ids
    ]

    # Return all valid suggestions
    return suggestions

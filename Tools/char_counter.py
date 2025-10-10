def count_characters(input_string: str, char_limit: int = 3532) -> dict:
    """
    Counts characters in a string and checks if it exceeds a specified limit.
    """
    total_characters = len(input_string)
    excess_characters = total_characters - char_limit

    result = {
        "total_characters": total_characters,
        "excess_message": (
            f"Character limit exceeded by {excess_characters} characters."
            if excess_characters > 0
            else "Within character limit."
        ),
    }
    return result
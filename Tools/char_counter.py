def count_characters(input_string: str) -> dict:
    total_characters = len(input_string)
    character_limit = 3560
    excess_characters = total_characters - character_limit

    result = {
        'total_characters': total_characters,
        'excess_message': f"Character limit exceeded by {excess_characters} characters."
                          if excess_characters > 0 else "Within character limit."
    }
    return result



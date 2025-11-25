def escape_html(text: str) -> str:
    """Escape HTML special characters in text to prevent XSS attacks."""
    import html
    return html.escape(text)
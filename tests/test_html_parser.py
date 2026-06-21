"""Tests for HTML parser module."""

from src.html_parser import clean_email_content, html_to_clean_text


class TestHtmlToCleanText:
    def test_basic_html(self):
        html = "<html><body><p>Hello World</p></body></html>"
        result = html_to_clean_text(html)
        assert "Hello World" in result

    def test_removes_scripts(self):
        html = "<p>Content</p><script>alert('xss')</script>"
        result = html_to_clean_text(html)
        assert "alert" not in result
        assert "Content" in result

    def test_removes_styles(self):
        html = "<style>body{color:red}</style><p>Visible</p>"
        result = html_to_clean_text(html)
        assert "color:red" not in result
        assert "Visible" in result

    def test_removes_tracking_pixels(self):
        html = '<p>Text</p><img width="1" height="1" src="track.gif">'
        result = html_to_clean_text(html)
        assert "track" not in result

    def test_removes_hidden_elements(self):
        html = '<p>Visible</p><div style="display:none">Hidden</div>'
        result = html_to_clean_text(html)
        assert "Visible" in result
        assert "Hidden" not in result

    def test_empty_html(self):
        assert html_to_clean_text("") == ""
        assert html_to_clean_text("   ") == ""

    def test_complex_newsletter_html(self):
        html = """
        <html>
        <head><style>.footer{color:gray}</style></head>
        <body>
            <div class="header"><h1>Newsletter Title</h1></div>
            <div class="content">
                <p>This is the main article content with important information.</p>
                <p>Second paragraph with more details about the topic.</p>
            </div>
            <div class="footer">Unsubscribe | Privacy Policy</div>
            <script>trackOpen()</script>
            <img width="1" height="1" src="pixel.gif">
        </body>
        </html>
        """
        result = html_to_clean_text(html)
        assert "Newsletter Title" in result
        assert "main article content" in result
        assert "trackOpen" not in result


class TestCleanEmailContent:
    def test_prefers_html(self):
        result = clean_email_content(
            html_body="<p>HTML version</p>",
            text_body="Plain text version"
        )
        assert "HTML version" in result

    def test_falls_back_to_text(self):
        result = clean_email_content(html_body="", text_body="Plain text only")
        assert result == "Plain text only"

    def test_empty_both(self):
        assert clean_email_content("", "") == ""

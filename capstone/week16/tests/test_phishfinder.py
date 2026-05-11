import pytest
from phishfinder import PhishingAnalyzer

@pytest.fixture
def analyzer():
    return PhishingAnalyzer(indicators={}, whitelist=[])

@pytest.fixture
def sample_email():
    return {
        "email_id": "1",
        "headers": {
            "from": "test@test.com",
            "reply_to": "test@test.com",
            "received": []
        },
        "body": {
            "text": "please verify your password immediately",
            "html": "<a href=\"http://evil.com\">click</a>"
        },
        "attachments": []
    }

# ------------------------
# NORMAL CASE
# ------------------------
def test_analyze_normal_email(analyzer, sample_email):
    result = analyzer.analyze_email(sample_email)
    
    assert result["email_id"] == "1"
    assert result["score"] >= 1
    assert "findings" in result

# ------------------------
# EDGE CASE (empty email)
# ------------------------
def test_empty_email(analyzer):
    result = analyzer.analyze_email({})
    
    assert result["score"] == 0
    assert result["verdict"] == "low risk"

# ------------------------
# INVALID INPUT
# ------------------------
def test_invalid_email_type(analyzer):
    with pytest.raises(Exception):
        analyzer.analyze_email(None)

# ------------------------
# URL EXTRACTION TEST
# ------------------------
def test_url_extraction(analyzer, sample_email):
    result = analyzer.analyze_email(sample_email)
    
    assert len(result["iocs"]["urls"]) > 0

# ------------------------
# ATTACHMENT DETECTION
# ------------------------
def test_suspicious_attachment(analyzer):
    email = {
        "email_id": "2",
        "headers": {},
        "body": {"text": "", "html": ""},
        "attachments": [{"filename": "virus.exe"}]
    }

    result = analyzer.analyze_email(email)

    assert result["score"] >= 3
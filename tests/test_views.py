"""This module tests the views of the website."""

from rep import app


def test_home_page():
    """Return 200 as status code on landing home page"""
    response = app.test_client().get('/')
    assert response.status_code == 200


def test_dashboard():
    """Should redirect (302) user because login is required"""
    response = app.test_client().get('/movesdata')
    assert response.status_code == 302


def test_logout():
    """Return 200 because user is instantly logged out"""
    response = app.test_client().get('/logout')
    assert response.status_code == 302

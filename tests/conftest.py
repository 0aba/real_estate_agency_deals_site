from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.remote.webdriver import WebDriver
from django.contrib.auth.models import AbstractUser
from django.core.management import call_command
from django.contrib.auth import get_user_model
from typing import Generator, Optional
from django.db import IntegrityError
from selenium import webdriver
import pytest
import uuid
import os


@pytest.fixture(scope='session', params=['chrome', 'firefox'])
def browser(request) -> Generator[WebDriver, None, None]:
    """
    Fixture for creating a browser object for testing.
    """
    browser_name: str = request.param
    
    driver: Optional[WebDriver] = None
    
    try:
        if browser_name == 'firefox':
            options = FirefoxOptions()
            options.add_argument('--headless')
            driver = webdriver.Firefox(options=options)
        elif browser_name == 'chrome':
            options = ChromeOptions()
            options.add_argument('--no-sandbox')
            driver = webdriver.Chrome(options=options)
        
        yield driver
    finally:
        if driver: driver.quit()

@pytest.fixture(scope="function", autouse=True)
def cleanup_cookies(browser) -> Generator[None, None, None]:
    """
    Fixture for deleting cookies when test is completed.
    """
    browser.delete_all_cookies()

@pytest.fixture(scope='function')
def flush_database() -> Generator[None, None, None]:
    """
    Fixture for cleaning the database using Django flush.
    """
    # INFO! Run test
    if os.getenv('MOD') != 'TEST': raise Exception('Cannot run database cleanup fixture for non-test environment')
    yield
    # INFO! End test
    call_command('flush', '--noinput')

def create_test_verify_user(username: str, password: str, is_superuser: bool = False) -> AbstractUser:
    """
    Creates a test user with a verified email via management commands.
    """
    if os.getenv('MOD') != 'TEST': raise Exception('Unable to change database for non-test environment')
    
    try:
        test_user = get_user_model().objects.create_user(
            username=username, 
            password=password, 
            email=f'{str(uuid.uuid4())[:8]}@fake.fake', 
            verification_email=True
        )
    except IntegrityError as e:
        error_msg = str(e)
        if '(username)=' in error_msg:
            raise Exception('Username already exists')
        elif '(email)=' in error_msg:
            raise Exception('The generated email already existed, which is why the account was not created')
        else:
            raise Exception('Could not create user due to an integrity error')

    if is_superuser:
        test_user.is_superuser = True
        test_user.save()
    
    return test_user

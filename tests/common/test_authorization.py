from ..conftest import browser, flush_database, create_test_verify_user
from selenium.webdriver.common.by import By


def test_login_account(browser , live_server, flush_database):
    """
    Test for the "Account Login" test case.
    """
    username: str = 'user1'
    password: str = 'o3m4b2!m'
    _ = create_test_verify_user(username, password)

    browser.get(live_server.url)
    
    # Cause №1
    login_button = browser.find_element(By.CSS_SELECTOR, 'a.btn-header[href="/user/login/"]')
    login_button.click()
    # Effect №1
    assert browser.current_url.endswith('/user/login/')
    
    # Cause №2
    username_input = browser.find_element(By.ID, 'id_username')
    username_input.send_keys(username)

    password_input = browser.find_element(By.ID, 'id_password')
    password_input.send_keys(password)
    # Effect №2
    assert username_input.get_attribute('value') == username
    assert password_input.get_attribute('value') == password

    # Cause №3
    submit_button = browser.find_element(By.CSS_SELECTOR, 'button.form-button')
    submit_button.click()
    # Effect №3
    _ = browser.find_element(By.CSS_SELECTOR, f'a.btn-header[href="/user/profile/{username}/"]')  # INFO! If the test fails, there is an error. 

def test_invalid_login_account(browser, live_server):
    """
    Test for the "Login Error for a Non-Existent Account" test case.
    """
    username: str = 'user1'
    password: str = 'o3m4b2!m'
    
    browser.get(live_server.url)
    
    # Cause №1
    login_button = browser.find_element(By.CSS_SELECTOR, 'a.btn-header[href="/user/login/"]')
    login_button.click()
    # Effect №1
    assert browser.current_url.endswith('/user/login/')
    
    # Cause №2
    username_input = browser.find_element(By.ID, 'id_username')
    username_input.send_keys(username)

    password_input = browser.find_element(By.ID, 'id_password')
    password_input.send_keys(password)
    # Effect №2
    assert username_input.get_attribute('value') == username
    assert password_input.get_attribute('value') == password

    # Cause №3
    submit_button = browser.find_element(By.CSS_SELECTOR, 'button.form-button')
    submit_button.click()
    # Effect №3
    _ = browser.find_element(By.CSS_SELECTOR, 'ul.errorlist.nonfield')  # INFO! If the test fails, there is an error. 

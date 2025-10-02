from ..conftest import browser, flush_database, create_test_verify_user, login_user
from selenium.webdriver.common.by import By


def test_change_profile_info(browser, live_server, flush_database):
    """
    Test for the "Change personal profile information" test case.
    """
    username: str = 'user1'
    password: str = 'o3m4b2!m'
    last_name: str = 'l'
    first_name: str = 'f'
    patronymic: str = 'p'
    phone: str = '71234567890'
    about: str = 'a' * 512

    _ = create_test_verify_user(username, password)

    browser.get(live_server.url)
    login_user(browser, username, password)

    header_link_profile = browser.find_element(By.CSS_SELECTOR, f'a.btn-header[href="/user/profile/{username}/"]')
    header_link_profile.click()
    
    # Cause №1
    change_profile_link = browser.find_element(By.CSS_SELECTOR, f'a.btn[href="/user/profile/{username}/change/"]')
    change_profile_link.click()
    # Effect №1
    assert browser.current_url.endswith(f'/user/profile/{username}/change/')
    
    # Cause №2
    last_name_input = browser.find_element(By.ID, 'id_last_name')
    last_name_input.send_keys(last_name)

    first_name_input = browser.find_element(By.ID, 'id_first_name')
    first_name_input.send_keys(first_name)

    patronymic_input = browser.find_element(By.ID, 'id_patronymic')
    patronymic_input.send_keys(patronymic)

    display_contacts = browser.find_element(By.ID, 'id_display_contacts')
    display_contacts.click()

    phone_input = browser.find_element(By.ID, 'id_phone')
    phone_input.send_keys(phone)

    about_input = browser.find_element(By.ID, 'id_about')
    about_input.send_keys(about)
    # Effect №2
    assert last_name_input.get_attribute('value') == last_name
    assert first_name_input.get_attribute('value') == first_name
    assert patronymic_input.get_attribute('value') == patronymic
    assert display_contacts.is_selected()
    assert phone_input.get_attribute('value') == phone
    assert about_input.get_attribute('value') == about

    # Cause №3
    submit_button = browser.find_element(By.CSS_SELECTOR, 'button.form-button')
    submit_button.click()
    # Effect №3
    _ = browser.find_element(By.CSS_SELECTOR, 'div.notification.success')  # INFO! If the test fails, there is an error. 

def test_invalid_change_profile_info(browser, live_server, flush_database):
    """
    Test for the "An error occurred while entering data when submitting a personal profile" test case.
    """
    username: str = 'user1'
    password: str = 'o3m4b2!m'
    last_name: str = 'l'
    first_name: str = 'f'
    patronymic: str = 'p'
    phone: str = '7'
    about: str = 'a'

    _ = create_test_verify_user(username, password)

    browser.get(live_server.url)
    login_user(browser, username, password)

    header_link_profile = browser.find_element(By.CSS_SELECTOR, f'a.btn-header[href="/user/profile/{username}/"]')
    header_link_profile.click()
    
    # Cause №1
    change_profile_link = browser.find_element(By.CSS_SELECTOR, f'a.btn[href="/user/profile/{username}/change/"]')
    change_profile_link.click()
    # Effect №1
    assert browser.current_url.endswith(f'/user/profile/{username}/change/')
    
    # Cause №2
    last_name_input = browser.find_element(By.ID, 'id_last_name')
    last_name_input.send_keys(last_name)

    first_name_input = browser.find_element(By.ID, 'id_first_name')
    first_name_input.send_keys(first_name)

    patronymic_input = browser.find_element(By.ID, 'id_patronymic')
    patronymic_input.send_keys(patronymic)

    display_contacts = browser.find_element(By.ID, 'id_display_contacts')
    display_contacts.click()

    phone_input = browser.find_element(By.ID, 'id_phone')
    phone_input.send_keys(phone)

    about_input = browser.find_element(By.ID, 'id_about')
    about_input.send_keys(about)
    # Effect №2
    assert last_name_input.get_attribute('value') == last_name
    assert first_name_input.get_attribute('value') == first_name
    assert patronymic_input.get_attribute('value') == patronymic
    assert display_contacts.is_selected()
    assert phone_input.get_attribute('value') == phone
    assert about_input.get_attribute('value') == about

    # Cause №3
    submit_button = browser.find_element(By.CSS_SELECTOR, 'button.form-button')
    submit_button.click()
    # Effect №3
    _ = browser.find_element(By.CSS_SELECTOR, 'ul.errorlist li')  # INFO! If the test fails, there is an error. 

def test_change_blacklist_user(browser, live_server, flush_database):
    """
    Test for the "Changing the blacklist status of another account" test case.
    """
    username1: str = 'user1'
    password1: str = 'o3m4b2!m'
    username2: str = 'user2'
    password2: str = 'o3m4f2!@'
    
    _ = create_test_verify_user(username1, password1)
    _ = create_test_verify_user(username2, password2)
    
    browser.get(live_server.url)
    login_user(browser, username1, password1)
    
    browser.get(f'{live_server.url}/user/profile/{username2}/')
    
    # Cause №1
    add_in_blacklist = browser.find_element(By.CSS_SELECTOR, f'a.btn[href="/user/add-bl-profile/{username2}/"]')
    add_in_blacklist.click()
    # Effect №1
    _ = browser.find_element(By.CSS_SELECTOR, f'a.btn[href="/user/del-bl-profile/{username2}/"]')  # INFO! If the test fails, there is an error. 

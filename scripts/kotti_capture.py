#!/usr/bin/env python
import os
import time
import contextlib
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image

# RPT = report to console
reporting = True
timing = True

start = time.time()

def RPT(message):
    if reporting:
        if timing:
            print "{0} -- {1:g} seconds".format(message, time.time() - start)
        else:
            print message

fruits = [{'name': u'Apple', 'tag': 'Core'},
          {'name': u'Avocado', 'tag': 'Tropical'},
          {'name': u'Banana', 'tag': 'Tropical'},
          {'name': u'Cantaloupe', 'tag': 'Melon'},
          {'name': u'Cherry', 'tag': 'Pit'},
          {'name': u'Grape', 'tag': 'Berry'},
          {'name': u'Kiwi', 'tag': 'Tropical'},
          {'name': u'Lemon', 'tag': 'Citrus'},
          {'name': u'Nectarine', 'tag': 'Pit'},
          {'name': u'Orange', 'tag': 'Citrus'},
          {'name': u'Peach', 'tag': 'Pit'},
          {'name': u'Pineapple', 'tag': 'Tropical'},
          {'name': u'Plum', 'tag': 'Pit'},
          {'name': u'Strawberry', 'tag': 'Berry'}]

TOOLBAR_HEIGHT = 40
MENU_HEIGHT = 40
BASE_URL = 'http://127.0.0.1:5000'

def log_in(browser, do_screencaptures):

    browser.get(BASE_URL + '/login')

    elem = browser.find_element_by_name("login")
    elem.send_keys("Admin")

    elem = browser.find_element_by_name("password")
    elem.send_keys("qwerty")

    if do_screencaptures:
        elem_footer = browser.find_element_by_tag_name('footer')
        save_screenshot_full(
            browser, 'logging_in.png', elem_top=None, elem_bottom=elem_footer)

    elem = browser.find_element_by_name("submit")
    elem.click()

    if do_screencaptures:
        elem_footer = browser.find_element_by_tag_name('footer')
        save_screenshot_full(
            browser, 'logged_in.png', elem_top=None, elem_bottom=elem_footer)

    RPT('logged in')

def log_out(browser):

    elem = browser.find_element_by_link_text('Administrator')
    elem.click()

    elem = browser.find_element_by_link_text('Logout')
    elem.click()

    RPT('logged out')

def not_logged_in(browser):

    browser.get(BASE_URL)

    elem_footer = browser.find_element_by_tag_name('footer')
    save_screenshot_full(browser, 'not_logged_in.png',
                         elem_top=None, elem_bottom=elem_footer)

def capture_menu(browser, image_name, link_text,
                 margin_division_factor, menu_height_factor,
                 submenu_link_text=None):

    elem = browser.find_element_by_link_text(link_text)
    elem.click()

    left, top = (elem.location['x'], elem.location['y'])

    menu_width, menu_height = (elem.size['width'], elem.size['height'])

    left -= menu_width / margin_division_factor
    top -= menu_height / margin_division_factor

    elem = browser.find_element_by_class_name("dropdown-menu")
    dropdown_menu_width, dropdown_menu_height = \
            (elem.size['width'], elem.size['height'])

    if submenu_link_text:

        elem = browser.find_element_by_link_text(submenu_link_text)
        hover = ActionChains(browser).move_to_element(elem)
        hover.perform()

        image_path = "../docs/images/{0}".format(image_name)
        browser.save_screenshot(image_path)

        im = Image.open(image_path)

        submenu_width, submenu_height = (elem.size['width'],
                                         elem.size['height'])

        width, height = \
                (dropdown_menu_width + submenu_width,
                 menu_height + \
                         menu_height_factor * dropdown_menu_height + \
                         menu_height_factor * submenu_height)

    else:

        image_path = "../docs/images/{0}".format(image_name)
        browser.save_screenshot(image_path)

        im = Image.open(image_path)

        width, height = \
                (dropdown_menu_width,
                 menu_height + menu_height_factor * elem.size['height'])

    box = (int(left), int(top),
           int(left + width + width/margin_division_factor),
           int(top + height + height/margin_division_factor))

    im = im.crop(box)

    im.save(image_path)

    RPT("{0} captured".format(image_path.split('/')[-1]))

def add_about_document(browser, title, description, body):

    wait = WebDriverWait(browser, 10)

    add_menu(browser)

    browser.find_element_by_class_name('brand').click()

    elem = browser.find_element_by_link_text('Add')
    elem.click()

    elem_footer = browser.find_element_by_tag_name('footer')
    save_screenshot_full(browser, 'add_about_actions_menu.png',
                         elem_top=None, elem_bottom=elem_footer)

    elem = browser.find_element_by_link_text("Document")
    elem.click()

    elem_title = browser.find_element_by_name('title')
    elem_title.send_keys(title)

    if description:
        elem_description = browser.find_element_by_id('deformField2')
        elem_description.send_keys(description)

    if body:
        elem_iframe = browser.switch_to_frame('deformField4_ifr')
        # Firefox bug:
        # http://code.google.com/p/selenium/issues/detail?id=2355
        elem_body = wait.until(lambda br: br.find_element_by_id('tinymce'))
        elem_body.send_keys(body)

    browser.switch_to_default_content()

    elem_save = browser.find_element_by_id('deformsave')
    save_screenshot_full(browser, 'add_about_save.png',
                         elem_top=None, elem_bottom=elem_save)
    elem_save.click()

    def save_was_successful(browser, wait):
        elem = wait.until(lambda br: br.find_element_by_id('messages'))
        for child in elem.find_elements_by_xpath('./*'):
            if 'Success' in child.text:
                return True
        return False

    wait.until(lambda browser: save_was_successful(browser, wait))

    elem_footer = wait.until(lambda br: br.find_element_by_tag_name('footer'))
    save_screenshot_full(browser, 'add_about_save_flash_message.png',
                         elem_top=None, elem_bottom=elem_footer)

    RPT('document {0} added'.format(title))

def add_fruit_rootstock_document(browser):

    title = 'Fruit Rootstock'
    description = ("The Fruit Stand on Main has a limited number of fruit "
                   "rootstock packs available.")
    tags = ['rootstock']
    body = """These are our current rootstocks:

Red Delicious
Bramley's Seedling
King-of-the-Pippins
MM.106 Rootstock

Email us if interested."""

    wait = WebDriverWait(browser, 10)

    elem = browser.find_element_by_link_text('Add')
    elem.click()

    elem = browser.find_element_by_link_text("Document")
    elem.click()

    elem_title = browser.find_element_by_name('title')
    elem_title.send_keys(title)

    if description:
        elem_description = browser.find_element_by_id('deformField2')
        elem_description.send_keys(description)

    if tags:
        elem_tags = wait.until(
                lambda br: br.find_element_by_id('deformField3'))
        elem_ul = wait.until(
                lambda br: br.find_element_by_class_name('tagit'))
        for tag in tags:
            for li in elem_ul.find_elements_by_tag_name('li'):
                if li.get_attribute('class') == 'tagit-new':
                    elem_input = li.find_element_by_tag_name('input')
                    elem_input.click()
                    elem_input.send_keys(tag + Keys.TAB)
                    time.sleep(.1)

    if body:
        elem_iframe = browser.switch_to_frame('deformField4_ifr')
        # Firefox bug:
        # http://code.google.com/p/selenium/issues/detail?id=2355
        elem_body = wait.until(lambda br: br.find_element_by_id('tinymce'))
        elem_body.send_keys(body)

    browser.switch_to_default_content()

    elem_save = browser.find_element_by_id('deformsave')
    save_screenshot_full(browser, 'add_fruit_rootstock_document_save.png',
                         elem_top=None, elem_bottom=elem_save)
    elem_save.click()

    def save_was_successful(browser, wait):
        elem = wait.until(lambda br: br.find_element_by_id('messages'))
        for child in elem.find_elements_by_xpath('./*'):
            if 'Success' in child.text:
                return True
        return False

    wait.until(lambda browser: save_was_successful(browser, wait))

    elem_footer = wait.until(lambda br: br.find_element_by_tag_name('footer'))
    save_screenshot_full(browser, 'add_fruit_rootstock_document_save_flash_message.png',
                         elem_top=None, elem_bottom=elem_footer)

    breadcrumbs(browser, 'add_fruit_rootstock_document_breadcrumbs.png')

    toolbar(browser, 'after_fruit_rootstock_document_toolbar.png')

    RPT('document {0} added'.format(title))

def add_fruits_document(browser):

    wait = WebDriverWait(browser, 10)

    description = ("Fruit Stand on Main has a variety of currently available "
                   "fruits.")
    add_document(browser,
                 "Fruits",
                 description,
                 ['rootstock', 'apple'],
                 "")

    elem_footer = wait.until(lambda br: br.find_element_by_tag_name('footer'))
    save_screenshot_full(browser, 'add_fruits_save_flash_message.png',
                         elem_top=None, elem_bottom=elem_footer)

def add_featured_fruits_document(browser):
    add_document(browser,
                 "Featured Fruits",
                 "Featured fruits at Fruit Stand on Main.",
                 ['featured'],
                 "")

def add_bramleys_seedling(browser):
    # BBC film of original Bramley tree: http://www.bbc.co.uk/news/uk-13764153

    browser.find_element_by_class_name('brand').click()

    add_featured_fruits_document(browser)

    add_bramleys_seedling_document(browser)

def add_bramleys_seedling_document(browser):

    # We are at "Featured Fruits".

    image_name = "frame_from_bbc_video.png"
    bramley_path = os.getcwd() + "/fruit_images/{0}".format(image_name)
    add_image(browser,
              "Bramley's Seedling Apple Tree",
              '',
              ['cooking', 'juicing', 'heirloom'],
              os.path.abspath(bramley_path))
    image_url = \
        "http://127.0.0.1:5000/featured-fruits/bramleys-seedling-apple-tree/image"

    click_main_nav_item(browser, 'Featured Fruits')

    title = "Bramley's Seedling"
    description = ("Bramley's Seedling is a popular cooking apple, native to "
                   "the UK.")
    tags = ['cooking', 'juicing', 'heirloom']
    body = ("All Bramley's Seedling apple trees can be traced to a "
            "single tree, still growing and producing, planted in 1809 "
            "by Mary Ann Brailsford, a young girl living in "
            "Nottinghamshire, England. The name Bramley comes from the "
            "man who bought the land where the tree grows in 1846.")

    wait = WebDriverWait(browser, 10)

    elem = browser.find_element_by_link_text('Add')
    elem.click()

    elem = browser.find_element_by_link_text("Document")
    elem.click()

    # Bug fix (See below where hang occurs if this script is not run):
    # http://stackoverflow.com/questions/11846339/chrome-webdriver-hungs-when-currently-selected-frame-closed
    # (See link to bug there).
    browser.execute_script("""(function() {
var domVar;
if (window.tinymce && window.tinymce.DOM) {
    domVar = window.tinymce.DOM
}
else if (window.tinyMCE && window.tinyMCE.DOM) {
    domVar = window.tinyMCE.DOM
}
else {
    return;
}
var tempVar = domVar.setAttrib;console.log(123)
domVar.setAttrib = function(id, attr, val) {
    if (attr == 'src' && typeof(val)== 'string' &&(val + "").trim().match(/javascript\s*:\s*("\s*"|'\s*')/)) {
        console.log("Cool");
        return;
    }
    else {
        tempVar.apply(this, arguments);
    }
}

}());""")

    elem_title = browser.find_element_by_name('title')
    elem_title.send_keys(title)

    elem_description = browser.find_element_by_id('deformField2')
    elem_description.send_keys(description)

    elem_tags = wait.until(
            lambda br: br.find_element_by_id('deformField3'))
    elem_ul = wait.until(
            lambda br: br.find_element_by_class_name('tagit'))
    for tag in tags:
        for li in elem_ul.find_elements_by_tag_name('li'):
            if li.get_attribute('class') == 'tagit-new':
                elem_input = li.find_element_by_tag_name('input')
                elem_input.click()
                elem_input.send_keys(tag + Keys.TAB)
                time.sleep(.1)

    elem_iframe = browser.switch_to_frame('deformField4_ifr')
    # Firefox bug:
    # http://code.google.com/p/selenium/issues/detail?id=2355
    elem_body = wait.until(lambda br: br.find_element_by_id('tinymce'))
    elem_body.send_keys(body)

    browser.switch_to_default_content()

    elem_save = browser.find_element_by_id('deformsave')
    save_screenshot_full(browser, 'adding_bramleys_seedling_document.png',
                         elem_top=None, elem_bottom=elem_save)

    browser.find_element_by_css_selector("span.mceIcon.mce_image").click()

    def image_dialog_appeared(browser, wait):
        elem = wait.until(
                lambda br: br.find_element_by_class_name('clearlooks2'))
        if elem:
            #elem.click()
            return True
        return False

    wait.until(lambda browser: image_dialog_appeared(browser, wait))

    tinymce_popup_frame = \
            browser.find_element_by_css_selector('iframe[id^="mce"]')

    browser.switch_to_frame(tinymce_popup_frame)

    elem_image = browser.switch_to_active_element()
    elem_image.send_keys(image_url)

    elem_alt = browser.find_element_by_id("alt")
    elem_alt.click()
    elem_alt.send_keys('Original tree in Nottinghamshire')

    elem_title = browser.find_element_by_id("title")
    elem_title.click()
    elem_title.send_keys('Screen Grab from BBC')

    save_screenshot_full(
            browser,
            'adding_bramleys_seedling_document_image_dialog.png',
            elem_top=None,
            elem_bottom=None)

    elem_insert = browser.find_element_by_name("insert")
    elem_insert.click()

    # Without the bug fix script above, the dialog comes down, but it hangs
    # here.

    browser.switch_to_default_content()

    elem_save = browser.find_element_by_id('deformsave')
    save_screenshot_full(
            browser,
            'adding_bramleys_seedling_document_image_in_body.png',
            elem_top=None,
            elem_bottom=elem_save)

    elem_save.click()

    def save_was_successful(browser, wait):
        elem = wait.until(lambda br: br.find_element_by_id('messages'))
        for child in elem.find_elements_by_xpath('./*'):
            if 'Success' in child.text:
                return True
        return False

    wait.until(lambda browser: save_was_successful(browser, wait))

    elem_footer = wait.until(lambda br: br.find_element_by_tag_name('footer'))
    save_screenshot_full(
            browser,
            'adding_bramleys_seedling_document_image_saved.png',
            elem_top=None,
            elem_bottom=elem_footer)

    RPT('document {0} added'.format(title))


def add_document(browser, title, description, tags, body):

    wait = WebDriverWait(browser, 10)

    elem = browser.find_element_by_link_text('Add')
    elem.click()

    elem = browser.find_element_by_link_text("Document")
    elem.click()

    elem_title = browser.find_element_by_name('title')
    elem_title.send_keys(title)

    if description:
        elem_description = browser.find_element_by_id('deformField2')
        elem_description.send_keys(description)

    if tags:
        elem_tags = wait.until(
                lambda br: br.find_element_by_id('deformField3'))
        elem_ul = wait.until(
                lambda br: br.find_element_by_class_name('tagit'))
        for tag in tags:
            for li in elem_ul.find_elements_by_tag_name('li'):
                if li.get_attribute('class') == 'tagit-new':
                    elem_input = li.find_element_by_tag_name('input')
                    elem_input.click()
                    elem_input.send_keys(tag + Keys.TAB)
                    time.sleep(.1)

    if body:
        elem_iframe = browser.switch_to_frame('deformField4_ifr')
        # Firefox bug:
        # http://code.google.com/p/selenium/issues/detail?id=2355
        elem_body = wait.until(lambda br: br.find_element_by_id('tinymce'))
        elem_body.send_keys(body)

    browser.switch_to_default_content()

    elem_save = browser.find_element_by_id('deformsave')
    elem_save.click()

    def save_was_successful(browser, wait):
        elem = wait.until(lambda br: br.find_element_by_id('messages'))
        for child in elem.find_elements_by_xpath('./*'):
            if 'Success' in child.text:
                return True
        return False

    wait.until(lambda browser: save_was_successful(browser, wait))

    RPT('document {0} added'.format(title))

def add_image(browser, title, description, tags, image_abspath):

    wait = WebDriverWait(browser, 10)

    elem = browser.find_element_by_link_text('Add')
    elem.click()

    elem = browser.find_element_by_link_text("Image")
    elem.click()

    elem_title = browser.find_element_by_name('title')
    elem_title.send_keys(title)

    if description:
        elem_description = browser.find_element_by_name('description')
        elem_description.send_keys(description)

    if tags:
        elem_tags = wait.until(
                lambda br: br.find_element_by_id('deformField3'))
        elem_ul = wait.until(
                lambda br: br.find_element_by_class_name('tagit'))
        for tag in tags:
            for li in elem_ul.find_elements_by_tag_name('li'):
                if li.get_attribute('class') == 'tagit-new':
                    elem_input = li.find_element_by_tag_name('input')
                    elem_input.click()
                    elem_input.send_keys(tag + Keys.TAB)
                    time.sleep(.1)

    elem = browser.find_element_by_name("upload")
    elem.send_keys(image_abspath)

    elem_save = browser.find_element_by_name('save')
    elem_save.click()

    def upload_was_successful(browser, wait):
        elem = wait.until(lambda br: br.find_element_by_id('messages'))
        for child in elem.find_elements_by_xpath('./*'):
            if 'Success' in child.text:
                return True
        return False

    wait.until(lambda browser: upload_was_successful(browser, wait))

    RPT('image {0} added'.format(title))

def search_and_capture_results(browser, image_name, query):

    wait = WebDriverWait(browser, 10)

    browser.find_element_by_class_name('brand').click()

    elem_search = browser.find_element_by_id('form-search')
    elem_input = elem_search.find_element_by_tag_name('input')
    elem_input.click()
    elem_input.send_keys(query + Keys.ENTER)

    def search_completed(browser, wait):
        elem = wait.until(lambda br: br.find_element_by_id('search-results'))
        return True if elem else False

    wait.until(lambda browser: search_completed(browser, wait))

    elem_footer = browser.find_element_by_tag_name('footer')
    save_screenshot_full(browser, image_name,
                         elem_top=None, elem_bottom=elem_footer)

    RPT("search results for {0} captured".format(query))

def toolbar(browser, target):

    elem_brand = browser.find_element_by_class_name('brand')
    elem_search = browser.find_element_by_id('form-search')
    elem_navbar = browser.find_element_by_class_name('navbar-inner')
    elem_nav = elem_navbar.find_element_by_class_name('nav')

    target_path = "../docs/images/{0}".format(target)

    browser.save_screenshot(target_path)

    crop_bbox_of_elems_and_save(target_path,
                                target_path,
                                [elem_brand, elem_search, elem_nav],
                                (10, 10, 10, 10))

    RPT("{0} captured".format(target))

def add_navigate_view(browser):

    elem_brand = browser.find_element_by_class_name('brand')

    elem = browser.find_element_by_link_text('Navigate')
    elem.click()

    time.sleep(2)

    browser.save_screenshot("../docs/images/navigate_view.png")

def breadcrumbs(browser, target):

    elem_breadcrumbs = browser.find_element_by_class_name('breadcrumb')

    target_path = "../docs/images/{0}".format(target)

    browser.save_screenshot(target_path)

    crop_bbox_of_elems_and_save(target_path,
                                target_path,
                                [elem_breadcrumbs,],
                                (10, 10, 10, 10))

    RPT("{0} captured".format(target))

def editor_bar(browser):

    if click_main_nav_item(browser, 'Fruits'):

        browser.save_screenshot('../docs/images/fruits_view.png')

        elem_state_span = browser.find_element_by_class_name('state-private')

        elem_administrator = \
                browser.find_element_by_link_text('Administrator')

        crop_bbox_of_elems_and_save('../docs/images/fruits_view.png',
                                    '../docs/images/editor_bar.png',
                                    [elem_state_span, elem_administrator],
                                    (10, 10, 10, 10))

        RPT('editor_bar captured')

def state_menu(browser):
    capture_menu(browser, "state_menu.png", "Private", 4, 3)

def add_menu(browser):
    capture_menu(browser, "add_menu.png", "Add", 4, 3)

def admin_menu(browser):
    capture_menu(browser, "admin_menu.png", "Administrator", 4, 3)

def publish_all(browser):
    for title in ['About', 'Featured Fruits', 'Fruit Rootstock', 'Fruits']:
        browser.find_element_by_class_name('brand').click()

        click_main_nav_item(browser, title)

        elem = browser.find_element_by_link_text('Private')
        elem.click()

        elem = browser.find_element_by_link_text('Make Public')
        elem.click()

def contents_view(browser):

    if click_main_nav_item(browser, 'Fruits'):

        elem = browser.find_element_by_link_text('Contents')
        elem.click()

        elem_copy = browser.find_element_by_name('copy')
        elem_hide = browser.find_element_by_name('hide')

        target_img = "../docs/images/contents_action_buttons.png"
        browser.save_screenshot(target_img)

        crop_bbox_of_elems_and_save(target_img,
                                    target_img,
                                    [elem_copy, elem_hide],
                                    (10, 10, 10, 10))

        elem_footer = browser.find_element_by_tag_name('footer')
        save_screenshot_full(browser, 'contents_view.png',
                             elem_top=None, elem_bottom=elem_footer)

        capture_menu(browser, "set_default_view.png", "Actions", 4, 3,
                 submenu_link_text='Set default view')

        RPT('contents views captured')
    else:
        RPT('PROBLEM with contents_action_buttons capture')

def fruits_view(browser):
    click_main_nav_item(browser, 'Fruits')

    elem_footer = browser.find_element_by_tag_name('footer')
    save_screenshot_full(browser, 'fruits_view.png',
                         elem_top=None, elem_bottom=elem_footer)

def set_default_view(browser, default_view):
    wait = WebDriverWait(browser, 10)

    click_main_nav_item(browser, 'Fruits')

    elem = browser.find_element_by_link_text("Actions")
    elem.click()

    elem = wait.until(
            lambda br: br.find_element_by_link_text("Set default view"))
    hover = ActionChains(browser).move_to_element(elem)
    hover.perform()

    elem = browser.find_element_by_link_text(default_view)
    elem.click()

def search_on_tropical_tag(browser):

    click_main_nav_item(browser, 'Fruits')

    elem = browser.find_element_by_link_text("Pineapple")
    elem.click()

    elem_footer = browser.find_element_by_tag_name('footer')
    save_screenshot_full(browser, 'pineapple.png',
                         elem_top=None, elem_bottom=elem_footer)

    elem = browser.find_element_by_link_text("Tropical")
    elem.click()

    elem_footer = browser.find_element_by_tag_name('footer')
    save_screenshot_full(browser, 'items_with_tropical_tag.png',
                         elem_top=None, elem_bottom=elem_footer)

def delete_about_document(browser):

    wait = WebDriverWait(browser, 10)

    if click_main_nav_item(browser, 'About'):

        elem_footer = browser.find_element_by_tag_name('footer')
        save_screenshot_full(browser, 'default_about.png',
                             elem_top=None, elem_bottom=elem_footer)

        elem_actions = \
                wait.until(lambda br: br.find_element_by_link_text('Actions'))
        elem_actions.click()

        save_screenshot_full(browser, 'default_about_actions_menu.png',
                             elem_top=None, elem_bottom=elem_footer)

        elem_delete = \
                wait.until(lambda br: br.find_element_by_link_text('Delete'))
        elem_delete.click()

        elem_delete = \
                wait.until(lambda br: br.find_element_by_name('delete'))

        # There is no footer on the confirmation page.
        save_screenshot_full(browser,
                             'default_about_delete_confirmation.png',
                             elem_top=None,
                             elem_bottom=elem_delete)

        elem_delete.click()

        elem_footer = browser.find_element_by_tag_name('footer')
        save_screenshot_full(browser, 'default_about_delete_flash_message.png',
                             elem_top=None, elem_bottom=elem_footer)

# Hangs in Chrome without bug fix. With Firefox, can't even get this far,
# because of bug with adding text to tinymce body.
def edit_about_document(browser):

    wait = WebDriverWait(browser, 10)

    # The goal of this edit is to make the phrase "current fruits" in the existing
    # body text into a link to the "Fruits" document.

    if click_main_nav_item(browser, 'About'):
        browser.get(BASE_URL + "/about/@@edit")

        # Grab this while we are here, then step back to 'About'.
        state_menu(browser)

        browser.get(BASE_URL + "/about/@@edit")

        elem_save = wait.until(lambda br: br.find_element_by_id('deformsave'))
        save_screenshot_full(browser, 'edit_about_document_edit.png',
                             elem_top=None, elem_bottom=elem_save)

        # Bug fix (See below where hang occurs if this script is not run):
        # http://stackoverflow.com/questions/11846339/chrome-webdriver-hungs-when-currently-selected-frame-closed
        # (See link to bug there).
        browser.execute_script("""(function() {
var domVar;
if (window.tinymce && window.tinymce.DOM) {
    domVar = window.tinymce.DOM
}
else if (window.tinyMCE && window.tinyMCE.DOM) {
    domVar = window.tinyMCE.DOM
}
else {
    return;
}
var tempVar = domVar.setAttrib;console.log(123)
domVar.setAttrib = function(id, attr, val) {
    if (attr == 'src' && typeof(val)== 'string' &&(val + "").trim().match(/javascript\s*:\s*("\s*"|'\s*')/)) {
        console.log("Cool");
        return;
    }
    else {
        tempVar.apply(this, arguments);
    }
}

}());""")

        elem_deformField4 = browser.find_element_by_id('deformField4_tbl')
        elem_deformField4.click()

        elem_iframe = browser.switch_to_frame('deformField4_ifr')
        editor = browser.switch_to_active_element()
        editor.click()

        move_left_keys = [Keys.ARROW_LEFT for i in xrange(28)]
        move = ActionChains(browser).send_keys_to_element(
                editor, ''.join(move_left_keys))
        move.perform()

        shift_key_down = ActionChains(browser).key_down(Keys.SHIFT)
        shift_key_down.perform()

        move_right_keys = [Keys.ARROW_RIGHT for i in xrange(15)]
        selection = ActionChains(browser).send_keys_to_element(
                editor, ''.join(move_right_keys))
        selection.perform()

        # This SHIFT key_up doesn't take effect somehow, and another one
        # is needed later.
        shift_key_up = ActionChains(browser).key_up(Keys.SHIFT)
        shift_key_up.perform()

        browser.switch_to_default_content()

        wait = WebDriverWait(browser, 10)

        browser.find_element_by_css_selector("span.mceIcon.mce_link").click()

        def link_dialog_appeared(browser, wait):
            elem = wait.until(
                    lambda br: br.find_element_by_class_name('clearlooks2'))
            if elem:
                #elem.click()
                return True
            return False

        wait.until(lambda browser: link_dialog_appeared(browser, wait))

        tinymce_popup_frame = \
                browser.find_element_by_css_selector('iframe[id^="mce"]')

        browser.switch_to_frame(tinymce_popup_frame)

        elem_href = browser.switch_to_active_element()

        # For unknown reason, have to release SHIFT again.
        shift_key_up = ActionChains(browser).key_up(Keys.SHIFT)
        shift_key_up.perform()

        href_add = ActionChains(browser).send_keys_to_element(
                elem_href, BASE_URL + '/fruits')
        href_add.perform()

        save_screenshot_full(browser, 'edit_about_document_adding_link_url.png',
                             elem_top=None, elem_bottom=None)

        elem_insert = browser.find_element_by_name("insert")
        elem_insert.click()

        # Without the bug fix script above, the dialog comes down, but it hangs
        # here, with the new link looking swell in the editor.

        browser.switch_to_default_content()

        browser.find_element_by_id("deformsave").click()

        save_screenshot_full(
                browser,
                'edit_about_document_with_link_to_fruits_document.png',
                elem_top=None, elem_bottom=None)


def edit_front_page(browser, title, description, body):

    wait = WebDriverWait(browser, 10)

    elem = browser.find_element_by_link_text('Edit')
    elem.click()

    elem_title = browser.find_element_by_name('title')
    elem_title.clear()
    elem_title.send_keys(title)

    if description:
        elem_description = browser.find_element_by_id('deformField2')
        elem_description.clear()
        elem_description.send_keys(description)

    if body:
        elem_iframe = browser.switch_to_frame('deformField4_ifr')
        # Firefox bug:
        # http://code.google.com/p/selenium/issues/detail?id=2355
        elem_body = wait.until(lambda br: br.find_element_by_id('tinymce'))
        elem_body.clear()
        elem_body.send_keys(body)

    browser.switch_to_default_content()

    elem_save = browser.find_element_by_id('deformsave')
    save_screenshot_full(browser, 'edit_front_page_save.png',
                         elem_top=None, elem_bottom=elem_save)
    elem_save.click()

    def save_was_successful(browser, wait):
        elem = wait.until(lambda br: br.find_element_by_id('messages'))
        for child in elem.find_elements_by_xpath('./*'):
            if 'Your changes have been saved' in child.text:
                return True
        return False

    wait.until(lambda browser: save_was_successful(browser, wait))

    elem_footer = wait.until(lambda br: br.find_element_by_tag_name('footer'))
    save_screenshot_full(browser, 'edit_front_page_save_flash_message.png',
                         elem_top=None, elem_bottom=elem_footer)

    RPT('document {0} edited'.format(title))


#####################
# Utility Functions

def click_main_nav_item(browser, text):

    wait = WebDriverWait(browser, 10)

    browser.switch_to_default_content()

    elem_main_nav = wait.until(lambda br: br.find_element_by_link_text(text))

    if elem_main_nav:
        elem_main_nav.click()
        RPT(text + ' clicked')
        return True

    return False

def add_fruits_content(browser):

    # Back to root.
    browser.find_element_by_class_name('brand').click()

    add_fruit_rootstock_document(browser)

    # Back to root.
    browser.find_element_by_class_name('brand').click()

    add_fruits_document(browser)

    for fruit in fruits:
        if click_main_nav_item(browser, 'Fruits'):
            image_name = "{0}_1200.jpg".format(fruit['name'])
            fruit_path = os.getcwd() + "/fruit_images/{0}".format(image_name)
            add_image(browser,
                      fruit['name'],
                      '',
                      [fruit['tag']],
                      os.path.abspath(fruit_path))
        else:
            RPT('PROBLEM with adding content')

    contents_view(browser)

    set_default_view(browser, 'Folder view')

def save_screenshot_full(browser, image_name, elem_top=None, elem_bottom=None):

    if not elem_top:
        top = 0
    else:
        top = int(elem_top.location['y'] - 15)

    if not elem_bottom:
        bottom = 0
    else:
        bottom = int(elem_bottom.location['y'] +
                     elem_bottom.size['height'] + 15)

    wait = WebDriverWait(browser, 10)

    image_path = "../docs/images/{0}".format(image_name)

    browser.save_screenshot(image_path)

    crop_full_width_and_save(image_path, top, bottom, image_path)

    RPT("{0} captured".format(image_name))

def crop_full_width_and_save(source_img, top, bottom, target_img):

    im = Image.open(source_img)
    width, height = im.size

    if not top:
        top = 0
    if not bottom:
        bottom = height

    if top < 0:
        top = 0
    if bottom > height:
        bottom = height

    im = im.crop((0, top, width, bottom))
    im.save(target_img)

def crop_bbox_of_elems_and_save(source_img, target_img, elems, margins):

    xmin = min([elem.location['x'] for elem in elems])
    xmax = max([elem.location['x'] + elem.size['width'] for elem in elems])

    ymin = min([elem.location['y'] for elem in elems])
    ymax = max([elem.location['y'] + elem.size['height'] for elem in elems])

    left_margin, right_margin, top_margin, bottom_margin = margins

    im = Image.open(source_img)

    im_width, im_height = im.size

    left = xmin - left_margin
    right = xmax + right_margin
    top = ymin - top_margin
    bottom = ymax + bottom_margin

    if left < 0:
        left = xmin
    if right > im_width:
        right = im_width
    if top < 0:
        top = ymin
    if bottom > im_height:
        bottom = im_height

    area = im.crop((left, top, right, bottom))

    area.save(target_img)

################
# Main routine

doc_files = ['../docs/introduction/overview.rst',
             '../docs/introduction/users_and_roles.rst',
             '../docs/adding_content/documents.rst',
             '../docs/editing_content/contents_view.rst',
             '../docs/editing_content/view_selection.rst']

chrome_driver_path = "{0}/chromedriver".format(os.getcwd())

browser = webdriver.Chrome(chrome_driver_path)

# Set the browser to full size to avoid wrapping issues.
browser.maximize_window()

# This will capture: logging_in
#                    logged_in
log_in(browser, True)

# We have to pay attention to the order of ops somewhat, being careful about
# adding content before making screen captures that expect certain content to
# be there.

# This will capture: default_about
#                    default_about_actions_menu
#                    default_about_delete_confirmation
#                    default_about_delete_flash_message
delete_about_document(browser)

# This will capture: add_about_actions_menu
#                    add_about_save
#                    add_about_save_flash_message
about_body = """We have many fruits available. Choose the fruit you want.
Our normal schedule:

Monday - Friday, 8 AM - 6 PM
Saturday, 7 AM - 2 PM

We often update our list of current fruits.

Address:

Fruit Stand on Main
123 Main Street
Somewhere, SW 01010

Email: fruits@example.com

Phone: +1-509-555-0100"""

add_about_document(browser, "About",
                   "This website is for Fruit Stand on Main, founded 1985.",
                   about_body)

browser.find_element_by_class_name('brand').click()

front_page_body = """We are located downtown at a convenient location on the
corner of Main and 5th Street.

Our garden is next door. Come by anytime to see what new
fresh veggies are available.

Our Motto: We want to be your main squeeze! :)"""
edit_front_page(browser,
                "Fruit Stand on Main",
                "Our fruit stand is tried and new, and still growing.",
                front_page_body)

# Now that we are logged in,
add_bramleys_seedling(browser)

add_fruits_content(browser)

# Capture editor_bar:
editor_bar(browser)

edit_about_document(browser)

# Do captures that need all content:
toolbar(browser, 'toolbar.png')
add_navigate_view(browser)
fruits_view(browser)
search_and_capture_results(browser, 'search_results_for_pit.png', 'Pit')
search_and_capture_results(browser, 'search_results_for_fruit.png', 'fruit')
search_on_tropical_tag(browser)

# Scan docs for needed screen captures, coming in the form of image entries in
# the Sphinx docs. The image names should match names of functions explicitly
# called here.
#for doc_file in doc_files:
#    for line in open(doc_file):
#        if line.startswith('.. Image::'):
#            image_name = line[10:].strip()
#            if image_name not in ['logged_in', 'toolbar_anonymous',
#                                  'editor_bar', 'not_logged_in']:
#                func_name = image_name[len('../images/'):-4]
#                if func_name in globals():
#                    globals()[func_name](browser)
#                else:
#                    print 'Function', func_name, 'NOT FOUND.'

log_out(browser)

# Capture after we have logged out.
not_logged_in(browser)

# Capture a plain toolbar.
toolbar(browser, 'toolbar_anonymous.png')

# Log back in and publish, log back out, and then capture published.
log_in(browser, False)

publish_all(browser)

log_out(browser)

browser.find_element_by_class_name('brand').click()
elem_footer = browser.find_element_by_tag_name('footer')
save_screenshot_full(browser, 'published.png', elem_top=None, elem_bottom=elem_footer)

browser.quit()

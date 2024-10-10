import requests
from bs4 import BeautifulSoup as soup
from stopwatch import Stopwatch
import time
import json




class Task:
    def __init__(self, link, size_wanted, username, password):
        self.link = input("What is the url of the product page? Leave empty if using variants. ")
        self.size_wanted = input("What size do you want? ")
        self.username = input("what is your username?")
        self.password = input("What is your password?")
        self.session = requests.session()
        self.sizes_variants = None
        self.checkout_page_response = self.get_checkout_html()
        self.auth_token = self.get_auth_token()
        self.checkout_link = self.get_checkout_link()

    def get_sizes_in_stock(self, url):
        response = self.session.get(url)   # gets the product page that the user wants
        page_html = soup(response.text, 'html.parser')    # parses the product page and grabs html
        div = page_html.find("div", {'class': 'variants-wrapper clearfix'})  # finds the div which contains size info
        all_sizes = div.find_all('option')# finds size info
        self.sizes_variants = all_sizes
        sizes_in_stock = []
        for option in all_sizes:   # adds all available sizes into a list
            if option.has_attr('value'):
                size = option.text
                sizes_in_stock.append(size)
    
        return sizes_in_stock   # returns that list
    # print(get_sizes_in_stock(link))
    
    def add_to_cart(self, size, url):
        size_in_stock = False
        sizes_in_stock = get_sizes_in_stock(url) # grabs the sizes that are in stock
        if '- /' in sizes_in_stock[0]:    # checks if user's size is in stock
            size = '- / ' + size
        for element in sizes_in_stock:
            if size == element:
                size_in_stock = True
        print(size)
    
        if size_in_stock == False:
            print('Unfortunately, your size is out of stock.')
    
        if size_in_stock == True:
            for option in self.sizes_variants:
                if size == option.text:
                    variant = option['value']
                    variant = str(variant) # makes the variant a string so it can be used in the payload
            payload = {
                "id": variant,
                "quantity":"1"
            }
            endpoint_atc = 'https://undefeated.com/cart/add.js'  # post request that adds the product to cart
            response = self.session.post(endpoint_atc, data=payload)
            if response.status_code == 200:
                print('Added to cart')
            else:
                print('ATC error')
    
    
    
    def login(self):          # this function will login to undefeated
        endpoint1 = 'https://undefeated.com/account/login'          # gets the login page
        payload = {
            "form_type": "customer_login",
            "utf8": "✓",
            "customer[email]": self.username,
            "customer[password]": self.password
        }
        response_login = self.session.post(endpoint1, data=payload)          # logs in to undefeated
        if response_login.status_code == 200:
            print('logged in')
        else:
            print('Log in error.')
    
    
    def checkout(self):            # checks out 
        credit_card = {"credit_card":{"number":"0000 0000 0000 0000","name":"John Smith","month":4,"year":2023,"verification_value":"999"}}
        payment_page_link = self.checkout_link + '?previous_step=shipping_method&step=payment_method'
        checkout_page_html = self.session.get(payment_page_link)
        checkout_page_soup = soup(self.checkout_page_html.text, 'html.parser')
        ul = checkout_page_soup.find('div', {'data-gateway-group': 'direct'})
        payment_gateway = ul['data-select-gateway']
        print(checkout_link)
        send_payment_url = 'https://elb.deposit.shopifycs.com/sessions'
        card_info_response = self.session.post(send_payment_url, json=credit_card)
        print(card_info_response)
        if card_info_response.status_code == 200:
            print('Payment info entered!')
        cc_verify = card_info_response.json()
        print(cc_verify)
        cc_verify_id = cc_verify['id']
        price = checkout_page_soup.find('div', {'role':'status'})
        price = price.find('span')
        price = price['data-checkout-payment-due-target']
        price = int(price) + 1000
        payload_final = {
            "utf8": "✓",
            "_method": "patch",
            "authenticity_token": self.auth_token,
            "previous_step": "payment_method",
            "step":"",
            "s": str(cc_verify_id),
            "checkout[payment_gateway]": str(payment_gateway),
            "checkout[credit_card][vault]": 'false',
            "checkout[different_billing_address]": 'false',
            "checkout[remember_me]": "false",
            "checkout[remember_me]": "0",
            "checkout[vault_phone]": "+11111111111",
            "checkout[total_price]": str(price),
            "complete": "1",
            "checkout[client_details][browser_width]": "782",
            "checkout[client_details][browser_height]": "789",
            "checkout[client_details][javascript_enabled]": "1"
        }
    
        confirm_order_response = self.session.post(self.checkout_link, data=payload_final)
        if confirm_order_response.status_code == 200:
            print('Processing payment...')
        else:
            print('Payment failed')
    
    def get_checkout_html(self):
        checkout_page_response = self.session.get('https://undefeated.com/checkout') # gets checkout info and parses the auth token
        return checkout_page_response
    
    
    def get_auth_token(self):
        checkout_html = soup(self.checkout_page_response.text, 'html.parser')
        input = checkout_html.find_all('input')[2]
        auth_token = input.get('value')
        return auth_token
    
    def get_checkout_link(self):
        checkout_link_headers = self.checkout_page_response.headers  # grabs the queue bypass link from the response header
        queue_bypass_link = checkout_link_headers['Set-Cookie']
        queue_bypass_link = str(queue_bypass_link).split(';')[3]
        queue_bypass_link = queue_bypass_link.split(' ')[1]
        queue_bypass_link = queue_bypass_link.split('=')[1]
        checkout_link = 'https://undefeated.com' + queue_bypass_link
        return checkout_link
    
    
    
    def enter_shipping_info(self):
        shipping_payload = {
            "utf8": "✓",
            "_method": "patch",
            "authenticity_token": str(self.auth_token),
            "previous_step": "contact_information",
            "step": "shipping_method",
            "checkout[email]": "example@gmail.com",
            "checkout[buyer_accepts_marketing]": "0",
            "checkout[shipping_address][first_name]": "John",
            "checkout[shipping_address][last_name]": "Smith",
            "checkout[shipping_address][company]": "",
            "checkout[shipping_address][address1]": "1111 Road Lane",
            "checkout[shipping_address][address2]": "",
            "checkout[shipping_address][city]": "City",
            "checkout[shipping_address][country]": "Country",
            "checkout[shipping_address][province]": "State",
            "checkout[shipping_address][zip]": "111111",
            "checkout[shipping_address][phone]": "(111) 111-111",
            "checkout[shipping_address][id]": "",
            "checkout[shipping_address][first_name]": "John",
            "checkout[shipping_address][last_name]": "Smith",
            "checkout[shipping_address][company]": "",
            "checkout[shipping_address][country]": "Country",
            "checkout[shipping_address][zip]": "111111",
            "checkout[shipping_address][province]": "state",
            "checkout[shipping_address][city]": "city",
            "checkout[shipping_address][address1]": "1111 Road Lane",
            "checkout[shipping_address][address2]": "",
            "checkout[shipping_address][phone]": "(111) 111-1111",
            "button": "",
            "checkout[client_details][browser_width]": "782",
            "checkout[client_details][browser_height]": "789",
            "checkout[client_details][javascript_enabled]": "1"
        }
        queue_bypass_response = self.session.post(self.checkout_link, data=shipping_payload)
        if queue_bypass_response.status_code == 302:
            print('Shipping info entered!')
    
    
    def select_shipping_method(self):
        shipping_method_payload = {
            "utf8": "✓",
            "_method": "patch",
            "authenticity_token": self.auth_token,
            "previous_step": "shipping_method",
            "step": "payment_method",
            "checkout[shipping_rate][id]": "shopify-UPS%20Ground-10.00",
            "button": "",
            "checkout[client_details][browser_width]": "799",
            "checkout[client_details][browser_height]": "789",
            "checkout[client_details][javascript_enabled]": "1"
        }
        shipping_method_response = self.session.post(self.checkout_link, data=shipping_method_payload)
        if shipping_method_response.status_code == 200:
            print('Shipping method selected!')
    
    
    
    def run(self):
        self.add_to_cart(self.size_wanted, self.link)
        self.login(self.username, self.password)
        self.enter_shipping_info()
        self.select_shipping_method()
        self.checkout()



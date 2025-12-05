import asyncio
import random
import time
import os
import pandas as pd

from ollama import chat
from ollama import ChatResponse

from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import dotenv

dotenv.load_dotenv()


# HELPER FUNCTIONS 
async def human_option_select(page, dropdown_selector, option_text):
    dropDownList = page.locator(dropdown_selector)
    await dropDownList.select_option(option_text)
    
async def human_button_click(page, selector=None, has_text=None ,exact_text=None, check_exists=False):
    if exact_text:
        element = page.get_by_text(exact_text, exact=False)
    elif has_text:
        element = page.locator(selector, has_text=has_text).first
    elif selector:
        element = page.locator(selector).first
    else:
        console.log("No selector provided")
        return
    
    if check_exists:
        try:
            # Wait up to 3000ms (3 seconds) for the element to appear
            await element.wait_for(state="visible", timeout=3000)
        except:
            # If it times out, print message and STOP function here
            print(f"The name '{exact_text or selector}' is not there.")
            return
            
    await element.hover()
    
    await asyncio.sleep(random.uniform(0.3, 0.7))
    
    await element.click()

async def human_type(page, selector, text):
    element = page.locator(selector).first

    await element.hover()
    await asyncio.sleep(random.uniform(0.2,0.5))

    await element.click()

    # Clear the field by selecting all and deleting (human-like behavior)
    await page.keyboard.press("Control+a")
    await asyncio.sleep(random.uniform(0.1, 0.2))

    await element.type(text, delay=random.randint(50,150))

async def get_human_name(description):
    response: ChatResponse = chat(model='gemma3', messages=[
  {
    'role': 'user',
    'content': 'output the persons name and surname in all upper case with turkish characters exactly as written' + description + ' if there is no name output ERROR: 404',
  },
])
    
    return response['message']['content']

async def get_payment_type(description, payment_amount):
    1600 uygulama sinav harci
    1200 yazili sinav
    1000 saglik belge ucreti
    2000 ozel ders fiyatlandirma, genelde 2 ders aliniyor,
    basarisiz aday egitimi 4000
    taksit 
    
    #sure payment types
    if int(payment_amount)==1000:
        return "BELGE ÜCRETİ"
    elif int(payment_amount)==1200:
        return "YAZILI SINAV HARCI"
    elif int(payment_amount)==1600:
        return "UYGULAMA SINAV HARCI"


    response: ChatResponse = chat(model='gemma3', messages=[
  {
    'role': 'user',
    'content': 'Your task is to look at the description and only output the types of payment. There are 6 types of payments: TAKSİT, YAZILI SINAV HARCI, UYGULAMA SINAV HARCI, BAŞARISIZ ADAY EĞİTİMİ, ÖZEL DERS, BELGE ÜCRETİ . There might be multiple types of payment in one go, make sure to specify each one you see. Description: ' + description + ' if you cant identify from the text output ERROR: 404',
  },
])
    
    return response['message']['content']
async def golden_PaymentPaid(page, name_surname, collection_type, amount):
    await human_button_click(page, "a.btn.bg-orange", has_text="KURSİYER ARA")
        
    await asyncio.sleep(random.uniform(1.7, 3.7))
    
    await human_type(page, "#txtaraadi", name_surname)
    
    await asyncio.sleep(random.uniform(0.8, 1.8))
    
    await page.keyboard.press("Enter")
    
    await asyncio.sleep(random.uniform(1.7, 3.7))
    
    await human_button_click(page, "a", has_text=name_surname)
    
    await asyncio.sleep(random.uniform(1.7, 3.7))
    
    await human_button_click(page, "a:visible", has_text="ÖDEME")

    await asyncio.sleep(random.uniform(0.8, 1.8))
    
    await human_button_click(page, "#btnyeniodeme")
    
    await asyncio.sleep(random.uniform(1.1, 3.7))
    
    await human_option_select(page, "#yenitahsilat_borctipi", collection_type)
    
    await asyncio.sleep(random.uniform(0.9, 3.1))
    
    await human_type(page, "#yenitahsilat_tutar", str(amount))
    
    await asyncio.sleep(random.uniform(0.7, 2.1))
    
    await human_button_click(page, "button", has_text="ÖDETTİR")
    
    await asyncio.sleep(random.uniform(1.6, 3.1))
    
    is_bot = await page.evaluate("navigator.webdriver")

async def golden_PaymentOwed(page, name_surname, collection_type, amount):
    await human_button_click(page, "a.btn.bg-orange", has_text="KURSİYER ARA")
        
    await asyncio.sleep(random.uniform(1.7, 3.7))
    
    await human_type(page, "#txtaraadi", name_surname)
    
    await asyncio.sleep(random.uniform(0.8, 1.8))
    
    await page.keyboard.press("Enter")
    
    await asyncio.sleep(random.uniform(1.7, 3.7))
    
    await human_button_click(page, "a", has_text=name_surname)
    
    await asyncio.sleep(random.uniform(1.7, 3.7))
    
    await human_button_click(page, "a:visible", has_text="ÖDEME")

    await asyncio.sleep(random.uniform(0.8, 1.8))
    
    await human_button_click(page, "#btnyeniborc")
    
    await asyncio.sleep(random.uniform(1.1, 3.7))
    
    await human_option_select(page, "#yeniborc_borctipi", collection_type)
    
    await asyncio.sleep(random.uniform(0.9, 3.1))
    
    await human_type(page, "#yeniborc_tutar", str(amount))
    
    await asyncio.sleep(random.uniform(0.7, 2.1))
    
    await human_button_click(page, "button.btn-success:visible", has_text="KAYDET")
    
    await asyncio.sleep(random.uniform(1.6, 3.1))

async def RPAexecutioner_readfile(filename, sheetname):
    dfs = pd.read_excel(filename, sheet_name=sheetname,header=14)
    people = dfs["Açıklama"]
    payments = dfs["Tutar"]
    tag = dfs["Etiket"]

    return [people, payments, tag]


async def RPAexecutioner_GoldenProcessStart(filename, sheetname):
    async with Stealth().use_async(async_playwright()) as playwright:
        chromium = playwright.chromium
        
        browser = await chromium.launch(headless=False)
        
        context = await browser.new_context()
        
        page = await context.new_page()
        
        response = await page.goto("https://kurs.goldennet.com.tr/giris.php")
        
        await human_type(page, "#kurumkodu", os.getenv("institution_code"))
        await asyncio.sleep(random.uniform(0.7, 1.9))
        
        await human_type(page, "#kullaniciadi", os.getenv("login"))
        await asyncio.sleep(random.uniform(1.1, 3.2))
        
        await human_type(page, "#kullanicisifresi", os.getenv("password"))
        await asyncio.sleep(random.uniform(0.9, 3.1))
        
        await human_button_click(page, "#btngiris")
        
        await asyncio.sleep(random.uniform(1.5, 4.1))
        
        payment_information = RPAexecutioner_readfile(filename, sheetname)

        for i in range(len(payment_information[0])):
            
            if payment_information[1][i].contains("-"):
                console.log(payment_information[1][i] +" Cost, not a received payment")
                continue
            if payment_information[2][i] != "Para Transferi":
                console.log("Not a payment transfer")
                continue

            name_surname = get_human_name(payment_information[0][i])
            if name_surname == "ERROR: 404":
                console.log("Error: name not found" + payment_information[0][i] + "was not attributed to any name")
                continue
            else:
                console.log("name found" + name_surname)

            payment_type = get_payment_type(payment_information[0][i],payment_information[1][i])

        
        
        
        is_bot = await page.evaluate("navigator.webdriver")
        
        print(f"Am I a bot? {is_bot}")
                
        
        await browser.close()

        
        

    
#asyncio.run(RPAexecutioner_PaymentOwed("Onur Çelik YZ Test", "TAKSİT", 6000))



print(asyncio.run(get_payment_type("FAST2923973105-ESRANUR GÖNEN-KURS ÜCRETİ +SINAV HARCI")))


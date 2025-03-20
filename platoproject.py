#imports
from scrapybara import Scrapybara
import asyncio
from playwright.async_api import async_playwright
import os

async def get_scrapybara_browser():
    client = Scrapybara(api_key=os.getenv("SCRAPYBARA_API_KEY"))
    instance = client.start_browser()
    return instance
async def retrieve_menu_items(instance, start_url: str) -> list[dict]:
    """
    :args:
    instance: the scrapybara instance to use
    url: the initial url to navigate to

    :desc:
    this function navigates to {url}. then, it will collect the detailed
    data for each menu item in the store and return it.

    (hint: click a menu item, open dev tools -> network tab -> filter for
            "https://www.doordash.com/graphql/itemPage?operation=itemPage")

    one way to do this is to scroll through the page and click on each menu
    item.

    determine the most efficient way to collect this data.

    :returns:
    a list of menu items on the page, represented as dictionaries
    """
    cdp_url = instance.get_cdp_url().cdp_url
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(cdp_url)
        page = await browser.new_page()

        await page.goto(start_url)

        # scroll to the bottom of the page to load all items 
        await page.locator('#footer').scroll_into_view_if_needed()
        await asyncio.sleep(2)

        # get all store items
        store_items = page.locator('li[data-testid^="store-item"]')
        count = await store_items.count()
        
        #print(count) - for debugging if needed
        menu_items = []
        # iterate through all items and get name, price, description
        for i in range(count):
            item = store_items.nth(i)

            # get item name, price + clean up
            nameL = item.locator('span[data-testid="rich-text"]').first
            name = await nameL.inner_text()
            name = name.strip()
            priceL = item.locator('span[data-testid="rich-text"]').nth(1)
            price = await priceL.inner_text()
            price = price.strip()

            # get item description + clean up
            descL = item.locator('div').nth(7)
            desc = await descL.locator('span').first.inner_text()
            desc = (desc.strip()).replace("\n", " ")

            menu_items.append({
                "name": name,
                "price": price,
                "description": desc
            })

            #print(name) #- for debugging if needed

        print(menu_items) #- for debugging if needed
        return menu_items

async def main():
    instance = await get_scrapybara_browser()

    try:
        await retrieve_menu_items(
            instance,
            "https://www.ubereats.com/store/dragon-wok-chinese-delights/7K2BItMEVjmnVVAi-Otjyw?diningMode=DELIVERY",
        )
    finally:
        # Be sure to close the browser instance after you're done!
        instance.stop()


if __name__ == "__main__":
    asyncio.run(main())
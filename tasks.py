from robocorp.tasks import task
from RPA.HTTP import HTTP
from robocorp import browser
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    '''
        Order robots from RobotSpareBin Industries Inc.
        Save order HTML receipt as PDF file.
        Save screenshot of Ordered robot.
        Embeds the screenshot of the robot to the PDF receipt.
        Create Zip archive of the receipt and PDF archive.
    '''
    browser.configure(
        slowmo=300,
    )
    open_robot_order_website()
    orders = get_orders()
    print(len(orders))
    for order in orders:
        close_annoying_banner()
        fill_form_and_submit(order)
    archive_receipts()
    

def archive_receipts():
    """Archives all the receipt pdfs into a single zip archive"""
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipt", "./output/receipts.zip")


def close_annoying_banner():
    """Close annoying banner on page load"""
    page = browser.page()
    page.click("text=OK")


def open_robot_order_website():
    """Open Bot Robot Page"""
    browser.goto('https://robotsparebinindustries.com/#/robot-order')


def get_orders():
    """Download and Read orders from CSV File"""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    return library.read_table_from_csv('orders.csv')

        
def fill_form_and_submit(order):
    """Fill order form and submit"""
    page = browser.page()
    page.select_option("#head", order.get('Head'))
    page.click(f"#id-body-{order.get('Body')}")
    page.fill("//input[@placeholder='Enter the part number for the legs']", order.get("Legs"))
    page.fill("#address", order.get("Address"))
    order_number = order.get("Order number")
    
    click_submit_button()
    pdf_path = store_receipt_as_pdf(order_number)
    screenshot_path = screenshot_robot(order_number)
    embed_screenshot_to_pdf(pdf_path, screenshot_path)
    click_order_another()


def click_submit_button():
    page = browser.page()
    while True:
        page.click("id=order", timeout=300)
        order = page.query_selector("#order-another")
        if order:
            break

    
def screenshot_robot(order_id):
    "Take page screenshot"
    screenshot_path = f'output/orders/robot-{order_id}.png'
    page = browser.page()
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path


def store_receipt_as_pdf(order_number):
    """Store Receipt of order as PDF"""
    page = browser.page()
    order_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = f"output/receipt/order-{order_number}.pdf"
    pdf.html_to_pdf(order_html, pdf_path)
    return pdf_path
    

def embed_screenshot_to_pdf(pdf_path, screenshot_path):
    """Embed screenshot to the pdf and save it"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path,
                                   source_path=pdf_path,
                                   output_path=pdf_path)


def click_order_another():
    """Store Receipt of order as PDF"""
    page = browser.page()
    page.click("id=order-another")

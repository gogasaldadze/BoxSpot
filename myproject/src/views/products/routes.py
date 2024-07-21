import os
from datetime import datetime
from wtforms.validators import ValidationError
from flask import request, send_file, Blueprint, render_template, redirect, url_for, flash
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from string import digits

from src.config import Config
from src.models import Prod
from src.views.products.forms import OrderForm



# Define the templates folder for Flask blueprint
TEMPLATES_FOLDER = os.path.join(Config.BASE_DIRECTORY, "templates", "products")
products_blueprint = Blueprint("products", __name__, template_folder=TEMPLATES_FOLDER)


# Register the Georgian font
font_path = os.path.join(Config.BASE_DIRECTORY, 'fonts', 'bpg_glaho_sylfaen.ttf')
pdfmetrics.registerFont(TTFont('BPGGlahoSylfaen', font_path))



@products_blueprint.route("/products/box/<category>")
def box_products(category):
    prod = Prod.query.filter_by(category=category).all()
    return render_template("box.html", prod=prod)


@products_blueprint.route("/products/detail/<int:product_id>", methods=["GET", "POST"])
def product_detail(product_id):
    product = Prod.query.get_or_404(product_id)
    form = OrderForm()  
    
    if form.validate_on_submit():
        if not form.data is digits:
            flash("ს.კ არ უნდა შეიცავდეს ასოებს")
        
        return redirect(url_for('products.box_products', category=product.category))
    
    return render_template("product_detail.html", product=product, form=form)

@products_blueprint.route("/products/paper/<category>")
def paper_products(category):
   
    prod = Prod.query.filter_by(category=category).all()
    return render_template("paper.html", prod=prod)

@products_blueprint.route("/products/accessories/<category>")
def accessories_products(category):
   
    prod = Prod.query.filter_by(category=category).all()
    return render_template("accessories.html", prod=prod)

# @products_blueprint.route("/products/detail/<int:product_id>")
# def product_detail(product_id):
 
#     product = Prod.query.get_or_404(product_id)
#     return render_template("product_detail.html", product=product)



@products_blueprint.route("/products/<int:product_id>/place_order", methods=["POST"])
def place_order(product_id):
   
    product = Prod.query.get_or_404(product_id)
    form = OrderForm()
    
    buyer_name = form.name
    buyer_id = form.id
    email = form.email
    quantity = form.quantity
    unit_price = product.price
    total_price = unit_price * quantity

    invoice_path = generate_pdf_invoice(product_id, buyer_name, buyer_id, email, quantity, unit_price, total_price)
    return send_file(invoice_path, as_attachment=True, download_name=os.path.basename(invoice_path))

def generate_pdf_invoice(product_id, buyer_name, buyer_id, buyer_address, quantity, unit_price, total_price):
    
    product = Prod.query.get_or_404(product_id)
    
    # Define the invoice directory and file path
    invoice_dir = os.path.join(Config.INVOICE_DIRECTORY, "invoices")
    os.makedirs(invoice_dir, exist_ok=True)
    invoice_filename = f"invoice_{product_id}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
    invoice_path = os.path.join(invoice_dir, invoice_filename)

    # Create a PDF document
    doc = SimpleDocTemplate(invoice_path, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)

    # Styles
    styles = getSampleStyleSheet()
    header_style = styles['Title']
    section_style = ParagraphStyle(name='Section', fontSize=12, fontName='BPGGlahoSylfaen', spaceAfter=10)
    normal_style = ParagraphStyle(name='Normal', fontSize=10, fontName='BPGGlahoSylfaen', spaceAfter=10)
    
    # Content
    content = []

    # Title
    content.append(Paragraph("Invoice", header_style))
    content.append(Paragraph(f"თარიღი: {datetime.now().strftime('%Y-%m-%d')}", normal_style))
    content.append(Paragraph(f"ვალუტა: ლარი", normal_style))
    content.append(Paragraph("<br />", normal_style))

    # Optional: Add a logo image to the PDF if exists
    image_path = os.path.join(Config.BASE_DIRECTORY, 'static', 'images', 'bspt.png')
    if os.path.exists(image_path):
        img = Image(image_path)
        img.drawHeight = 50
        img.drawWidth = 100
        content.append(img)

    # Seller Information
    content.append(Paragraph("გამყიდველის ინფორმაცია", section_style))
    content.append(Paragraph("სახელი:"  "ი /მ ,,ნათია დვალიშვილი" , normal_style))
    content.append(Paragraph("მისამართი: თბილისი, მე-5 პლატო, მე-3 კორპ. ბინა-30", normal_style))
    content.append(Paragraph("ტელეფონი: (+955)599541791", normal_style))
    content.append(Paragraph("საბანკო რეკვიზიტები: ს.ს. ,,საქართველოს ბანკი'' ა/ა GE96BG0000000498866105 ", normal_style))
    content.append(Paragraph("<br />", normal_style))

    # Buyer Information
    content.append(Paragraph("შემკვეთის ინფორმაცია", section_style))
    content.append(Paragraph(f"სახელი: {buyer_name}", normal_style))
    content.append(Paragraph(f"ს/კ: {buyer_id}", normal_style))
    content.append(Paragraph(f"მისამართი: {buyer_address}", normal_style))
    content.append(Paragraph("<br />", normal_style))

    # Invoice Table
    table_data = [
        ["#", "პროდუქტის აღწერა", "რაოდენობა", "ერთ.ფასი", "სულ"],
        [1, product.description, quantity, unit_price, total_price]
    ]
    
    table = Table(table_data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'BPGGlahoSylfaen'),
        ('FONTNAME', (0, 1), (-1, -1), 'BPGGlahoSylfaen'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
    ]))

    content.append(table)
    content.append(Paragraph("<br />", normal_style))
    
    # Total Amount
    content.append(Paragraph(f"სულ გადასახდელია: {total_price} ლარი", section_style))
    content.append(Paragraph("<br />", normal_style))
    
    # Footer
    content.append(Paragraph("უღრმეს მადლობას გიხდით შეკვეთისათვის!", normal_style))
    
    # Build PDF
    doc.build(content)
    
    return invoice_path

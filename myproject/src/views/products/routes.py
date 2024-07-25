import os
from datetime import datetime
from flask import request, send_file, Blueprint, render_template, redirect, url_for, flash

from reportlab.lib.pagesizes import letter
from flask_login import login_required, current_user
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from src.config import Config
from src.models import Prod, Order
from src.views.products.forms import OrderForm
from src.extensions import db

TEMPLATES_FOLDER = os.path.join(Config.BASE_DIRECTORY, "templates", "products")
products_blueprint = Blueprint("products", __name__, template_folder=TEMPLATES_FOLDER)

font_path = os.path.join(Config.BASE_DIRECTORY, 'fonts', 'bpg_glaho_sylfaen.ttf')
pdfmetrics.registerFont(TTFont('BPGGlahoSylfaen', font_path))

@products_blueprint.route("/products/<category>")
def products(category):
    prod = Prod.query.filter_by(category=category).all()
    return render_template("product.html", prod=prod)



@products_blueprint.route("/products/detail/<int:product_id>", methods=["GET", "POST"])
@login_required
def product_detail(product_id):
    product = Prod.query.get_or_404(product_id)
    form = OrderForm()  
    
    return render_template("product_detail.html", product=product, form=form)

@products_blueprint.route("/products/<int:product_id>/place_order", methods=["POST"])
@login_required
def place_order(product_id):
    product = Prod.query.get_or_404(product_id)
    form = OrderForm()

    if form.validate_on_submit():
        buyer_name = form.name.data
        buyer_id = form.id.data
        email = form.email.data
        quantity = form.quantity.data
        unit_price = product.price
        total_price = unit_price * quantity

        # Create Order instance
        new_order = Order(
            product_id=product.id,
            user_id=current_user.id,
            quantity=quantity,
            total_price=total_price,
            status='Pending'
        )

        # Save order to database
        db.session.add(new_order)
        db.session.commit()

        invoice_path = generate_pdf_invoice(product_id, buyer_name, buyer_id, email, quantity, unit_price, total_price)

        flash('თქვენი შეკვეთა მიღებულია')
        return send_file(invoice_path, as_attachment=True, download_name=os.path.basename(invoice_path))

    else:
        for errors in form.errors.values():
            for error in errors:
                flash(error)

    print(form.errors)
    return redirect(url_for('products.product_detail', product_id=product_id))


def generate_pdf_invoice(product_id, buyer_name, buyer_id, email, quantity, unit_price, total_price):
    product = Prod.query.get_or_404(product_id)
    
    
    invoice_dir = os.path.join(Config.INVOICE_DIRECTORY,"invoices")
    if not os.path.exists(invoice_dir):
        print(f"Directory does not exist: {invoice_dir}")
        os.makedirs(invoice_dir, exist_ok=True)
    else:
        print(f"Directory exists: {invoice_dir}")

    # Create file path
    invoice_filename = f"invoice_{current_user.username}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
    invoice_path = os.path.join(invoice_dir, invoice_filename)
    print(f"Invoice path: {invoice_path}")

    # Create PDF
    doc = SimpleDocTemplate(invoice_path, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)

    styles = getSampleStyleSheet()
    header_style = styles['Title']
    section_style = ParagraphStyle(name='Section', fontSize=12, fontName='BPGGlahoSylfaen', spaceAfter=10)
    normal_style = ParagraphStyle(name='Normal', fontSize=10, fontName='BPGGlahoSylfaen', spaceAfter=10)
    
    content = []
    content.append(Paragraph("Invoice", header_style))
    content.append(Paragraph(f"თარიღი: {datetime.now().strftime('%Y-%m-%d')}", normal_style))
    content.append(Paragraph(f"ვალუტა: ლარი", normal_style))
    content.append(Paragraph("<br />", normal_style))

    content.append(Paragraph("გამყიდველის ინფორმაცია", section_style))
    content.append(Paragraph("სახელი: ი /მ ,,ნათია დვალიშვილი''", normal_style))
    content.append(Paragraph("მისამართი: თბილისი, მე-5 პლატო, მე-3 კორპ. ბინა-30", normal_style))
    content.append(Paragraph("ტელეფონი: (+955)599541791", normal_style))
    content.append(Paragraph("საბანკო რეკვიზიტები: ს.ს. ,,საქართველოს ბანკი'' ა/ა GE96BG0000000498866105", normal_style))
    content.append(Paragraph("<br />", normal_style))

    content.append(Paragraph("შემკვეთის ინფორმაცია", section_style))
    content.append(Paragraph(f"სახელი: {buyer_name}", normal_style))
    content.append(Paragraph(f"ს/კ: {buyer_id}", normal_style))
    content.append(Paragraph(f"ელ-ფოსტა: {email}", normal_style))
    content.append(Paragraph("<br />", normal_style))

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
    
    content.append(Paragraph(f"სულ გადასახდელია: {total_price} ლარი", section_style))
    content.append(Paragraph("<br />", normal_style))
    
    content.append(Paragraph("უღრმეს მადლობას გიხდით შეკვეთისათვის!", normal_style))
    
    try:
        doc.build(content)
        print(f"Invoice successfully created at: {invoice_path}")
    except Exception as e:
        print(f"Error creating invoice: {e}")
    
    return invoice_path

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch

from src.config import Config
from src.models import Prod, Order, CartItem
from src.views.products.forms import OrderForm, AddToCartForm, RemoveFromCartForm, UpdateCartForm
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
    form = AddToCartForm()
    
    return render_template("product_detail.html", product=product, form=form)

@products_blueprint.route("/products/<int:product_id>/add_to_cart", methods=["POST"])
@login_required
def add_to_cart(product_id):
    product = Prod.query.get_or_404(product_id)
    form = AddToCartForm()
    
    if form.validate_on_submit():
        quantity = form.quantity.data
        
        # Check if the product is already in the cart
        cart_item = CartItem.query.filter_by(product_id=product.id, user_id=current_user.id).first()
        
        if cart_item:
            # Update the quantity if the item is already in the cart
            cart_item.quantity += quantity
        else:
            # Add new item to the cart
            cart_item = CartItem(product_id=product.id, product_name=product.name, user_id=current_user.id, quantity=quantity)
            db.session.add(cart_item)
        
        db.session.commit()
        flash('Product added to cart.')
    else:
        for errors in form.errors.values():
            for error in errors:
                flash(error)
    
    return redirect(url_for('products.product_detail', product_id=product_id))

@products_blueprint.route("/cart")
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', cart_items=cart_items)

@products_blueprint.route("/update_cart", methods=["POST"])
@login_required
def update_cart():
    item_id = request.form.get('item_id')
    quantity = request.form.get('quantity')

    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id == current_user.id:
        cart_item.quantity = quantity
        db.session.commit()
        flash('Cart updated successfully.')
    else:
        flash('Error updating cart.')

    return redirect(url_for('products.view_cart'))

@products_blueprint.route("/remove_from_cart/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id == current_user.id:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Product removed from cart!')
    else:
        flash('Error removing product from cart!')
    
    return redirect(url_for('products.view_cart'))

@products_blueprint.route("/order_confirmation")
@login_required
def order_confirmation():
    product_id = request.args.get('product_id')
    if not product_id:
        flash('Product ID is missing.')
        return redirect(url_for('products.view_cart'))

    success_message = "თქვენი შეკვეთა მიღებულია!"
    error_message = "დაფიქსირდა შეცდომა, გთხოვთ სცადოთ ხელახლა "

    return render_template(
        'order_confirmation.html',
        product_id=product_id,
        success=True,
        success_message=success_message,
        error_message=error_message
    )

@products_blueprint.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    form = OrderForm()
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        flash('თქვენი კალათა ცარიელია')
        return redirect(url_for('products.view_cart'))

    if form.validate_on_submit():
        # Store product_ids before deleting cart items
        product_ids = [item.product_id for item in cart_items]

        # Process the form data and create orders
        for item in cart_items:
            order = Order(
                product_id=item.product_id,
                product_name=item.product_name,
                user_id=current_user.id,
                user_name=form.name.data,
                quantity=item.quantity,
                total_price=item.quantity * item.product.price
            )
            db.session.add(order)

        db.session.commit()

        # Generate a single PDF invoice for all cart items
        generate_pdf_invoice(
            buyer_name=form.name.data,
            buyer_id=form.id.data,
            email=form.email.data,
            cart_items=cart_items
        )

        # Clear the cart after checkout
        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        flash('Order placed successfully.')
        # Pass the product_id of the first product in the cart for confirmation
        return redirect(url_for('products.order_confirmation', product_id=product_ids[0]))

    return render_template('checkout.html', form=form)


def generate_pdf_invoice(buyer_name, buyer_id, email, cart_items):
    invoice_dir = os.path.join(Config.INVOICE_DIRECTORY, "invoices")
    if not os.path.exists(invoice_dir):
        os.makedirs(invoice_dir)

    invoice_filename = f"invoice_{buyer_name}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
    invoice_path = os.path.join(invoice_dir, invoice_filename)

    doc = SimpleDocTemplate(invoice_path, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)

    # Define styles using the registered Georgian font
    header_style = ParagraphStyle(name='Header', fontSize=18, fontName='BPGGlahoSylfaen', spaceAfter=10, alignment=1)
    section_style = ParagraphStyle(name='Section', fontSize=12, fontName='BPGGlahoSylfaen', spaceAfter=10)
    normal_style = ParagraphStyle(name='Normal', fontSize=10, fontName='BPGGlahoSylfaen', spaceAfter=10)
    footer_style = ParagraphStyle(name='Footer', fontSize=8, fontName='BPGGlahoSylfaen', alignment=1)

    # Path to the logo image
    logo_path = os.path.join(Config.BASE_DIRECTORY, 'static', 'logo.png')

    content = []

    # Add logo
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2*inch, height=2*inch)
        logo.hAlign = 'LEFT'
        content.append(logo)

    content.append(Spacer(1, 12))
    content.append(Paragraph("Invoice", header_style))
    content.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", normal_style))
    content.append(Paragraph("Currency: ლარი", normal_style))
    content.append(Spacer(1, 12))

    content.append(Paragraph("გამყიდველის ინფორმაცია", section_style))
    content.append(Paragraph("სახელწოდება:ი /მ ,,ნათია დვალიშვილი   Natia Dvalishvili", normal_style))
    content.append(Paragraph("მისამართი: თბილისი მე-5 პლატო, მე-3 კორპ. ბ.30", normal_style))
    content.append(Paragraph("ნომერი: (+995)599541791", normal_style))
    content.append(Paragraph("საბანკო რეკვიზიტები: საქართველოს ბანკი, GE96BG0000000498866105", normal_style))
    content.append(Spacer(1, 12))

    content.append(Paragraph("მყიდველის ინფორმაცია", section_style))
    content.append(Paragraph(f"სახელწოდება: {buyer_name}", normal_style))
    content.append(Paragraph(f"საკადასტრო კოდი/პირადი ნომერი: {buyer_id}", normal_style))
    content.append(Paragraph(f"ელ-ფოსტა: {email}", normal_style))
    content.append(Spacer(1, 12))

    table_data = [["#", "პროდ. აღწერა", "რაოდ", "ერთ ფასი", "სულ"]]
    total_price = 0

    for index, item in enumerate(cart_items, start=1):
        product = Prod.query.get_or_404(item.product_id)
        item_total = item.quantity * item.product.price
        total_price += item_total
        table_data.append([index, product.description, item.quantity, item.product.price, item_total])
    
    table = Table(table_data, hAlign='LEFT', colWidths=[30, 250, 60, 60, 60])
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
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey)
    ]))

    content.append(table)
    content.append(Spacer(1, 12))
    
    content.append(Paragraph(f"სულ გადასახდელია: {total_price} ლარი", section_style))
    content.append(Spacer(1, 12))
    
    content.append(Paragraph("მადლობას გიხდით შეკვეთისათვის!", normal_style))
    content.append(Spacer(1, 24))

    # Footer
    content.append(Paragraph(" Boxspot | 23 Merab Kostava st.  | (+955)599541791 ", footer_style))

    try:
        doc.build(content)
        print(f"Invoice successfully created at: {invoice_path}")
    except Exception as e:
        print(f"Error creating invoice: {e}")
    
    return invoice_path

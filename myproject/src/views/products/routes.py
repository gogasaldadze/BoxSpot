from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

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
    # Logic to update cart items
    # Extract item_id and quantity from form data and update the cart
    item_id = request.form.get("item_id")
    quantity = request.form.get("quantity")

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


@products_blueprint.route("/checkout", methods=["POST"])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty.')
        return redirect(url_for('products.view_cart'))
    
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    for item in cart_items:
        order = Order(
            product_id=item.product_id,
            product_name=item.product_name,
            user_id=current_user.id,
            user_name=current_user.username,
            quantity=item.quantity,
            total_price=item.product.price * item.quantity
        )
        db.session.add(order)
    
    # Clear the cart after checkout
    CartItem.query.filter_by(user_id=current_user.id).delete()
    
    db.session.commit()
    flash('Order placed successfully.')
    
    # Generate PDF invoice
    for item in cart_items:
        generate_pdf_invoice(
            product_id=item.product_id,
            buyer_name=current_user.username,
            buyer_id=current_user.id,
            email=current_user.email,
            quantity=item.quantity,
            unit_price=item.product.price,
            total_price=item.product.price * item.quantity
        )
    
    return redirect(url_for('products.view_orders'))

def generate_pdf_invoice(product_id, buyer_name, buyer_id, email, quantity, unit_price, total_price):
    product = Prod.query.get_or_404(product_id)
    
    invoice_dir = os.path.join(Config.INVOICE_DIRECTORY, "invoices")
    if not os.path.exists(invoice_dir):
        os.makedirs(invoice_dir)

    invoice_filename = f"invoice_{current_user.username}_{datetime.now().strftime('%Y-%m-%d')}.pdf"
    invoice_path = os.path.join(invoice_dir, invoice_filename)

    doc = SimpleDocTemplate(invoice_path, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)

    styles = getSampleStyleSheet()
    header_style = styles['Title']
    section_style = ParagraphStyle(name='Section', fontSize=12, fontName='BPGGlahoSylfaen', spaceAfter=10)
    normal_style = ParagraphStyle(name='Normal', fontSize=10, fontName='BPGGlahoSylfaen', spaceAfter=10)
    
    content = []
    content.append(Paragraph("Invoice", header_style))
    content.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", normal_style))
    content.append(Paragraph("Currency: Lari", normal_style))
    content.append(Paragraph("<br />", normal_style))

    content.append(Paragraph("Seller Information", section_style))
    content.append(Paragraph("Name: Natia Dvalishvili", normal_style))
    content.append(Paragraph("Address: Tbilisi, 5th Plato, 3rd Corp. Apt. 30", normal_style))
    content.append(Paragraph("Phone: (+995)599541791", normal_style))
    content.append(Paragraph("Bank Details: Bank of Georgia, GE96BG0000000498866105", normal_style))
    content.append(Paragraph("<br />", normal_style))

    content.append(Paragraph("Buyer Information", section_style))
    content.append(Paragraph(f"Name: {buyer_name}", normal_style))
    content.append(Paragraph(f"ID: {buyer_id}", normal_style))
    content.append(Paragraph(f"Email: {email}", normal_style))
    content.append(Paragraph("<br />", normal_style))

    table_data = [
        ["#", "Product Description", "Quantity", "Unit Price", "Total"],
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
    
    content.append(Paragraph(f"Total Amount Due: {total_price} Lari", section_style))
    content.append(Paragraph("<br />", normal_style))
    
    content.append(Paragraph("Thank you for your order!", normal_style))
    
    try:
        doc.build(content)
        print(f"Invoice successfully created at: {invoice_path}")
    except Exception as e:
        print(f"Error creating invoice: {e}")
    
    return invoice_path

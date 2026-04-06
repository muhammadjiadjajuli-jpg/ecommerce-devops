from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.environ.get('DB_USER', 'user')}:{os.environ.get('DB_PASSWORD', 'password')}@{os.environ.get('DB_HOST', 'db')}:3306/{os.environ.get('DB_NAME', 'ecommerce')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
metrics = PrometheusMetrics(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    description = db.Column(db.String(200))

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'stock': p.stock,
        'description': p.description
    } for p in products])

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    product = Product(
        name=data['name'],
        price=data['price'],
        stock=data.get('stock', 0),
        description=data.get('description', '')
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product added successfully'}), 201

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            sample = [
                Product(name='Laptop', price=999.99, stock=10, description='High performance laptop'),
                Product(name='Mouse', price=29.99, stock=50, description='Wireless mouse'),
                Product(name='Keyboard', price=79.99, stock=30, description='Mechanical keyboard')
            ]
            for p in sample:
                db.session.add(p)
            db.session.commit()
    app.run(host='0.0.0.0', port=5000)

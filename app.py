from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store_inventory.db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Gerenciamento de Estoque</title>
</head>
<body>
    <h1>Gerenciamento de Estoque</h1>
    <form id="productForm">
        <input type="text" id="name" placeholder="Nome do Produto" required>
        <input type="number" id="quantity" placeholder="Quantidade" required>
        <input type="number" step="0.01" id="price" placeholder="Preço" required>
        <button type="submit">Adicionar Produto</button>
    </form>
    <table border="1">
        <thead>
            <tr>
                <th>ID</th>
                <th>Nome</th>
                <th>Quantidade</th>
                <th>Preço</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody id="productTable">
        </tbody>
    </table>

    <script>
        document.getElementById('productForm').addEventListener('submit', function(event) {
            event.preventDefault();
            const name = document.getElementById('name').value;
            const quantity = document.getElementById('quantity').value;
            const price = document.getElementById('price').value;

            fetch('/products', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, quantity, price })
            }).then(response => response.json())
              .then(data => {
                  loadProducts();
                  document.getElementById('productForm').reset();
              });
        });

        function loadProducts() {
            fetch('/products')
                .then(response => response.json())
                .then(data => {
                    const productTable = document.getElementById('productTable');
                    productTable.innerHTML = '';
                    data.forEach(product => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${product.id}</td>
                            <td>${product.name}</td>
                            <td>${product.quantity}</td>
                            <td>${product.price}</td>
                            <td>
                                <button onclick="deleteProduct(${product.id})">Excluir</button>
                            </td>
                        `;
                        productTable.appendChild(row);
                    });
                });
        }

        function deleteProduct(id) {
            fetch(`/products/${id}`, {
                method: 'DELETE'
            }).then(response => response.json())
              .then(data => {
                  loadProducts();
              });
        }

        window.onload = function() {
            loadProducts();
        }
    </script>
</body>
</html>
    ''')

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    result = [{"id": p.id, "name": p.name, "quantity": p.quantity, "price": p.price} for p in products]
    return jsonify(result)

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    new_product = Product(name=data['name'], quantity=data['quantity'], price=data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"id": new_product.id, "name": new_product.name, "quantity": new_product.quantity, "price": new_product.price})

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    product.name = data['name']
    product.quantity = data['quantity']
    product.price = data['price']
    db.session.commit()
    return jsonify({"id": product.id, "name": product.name, "quantity": product.quantity, "price": product.price})

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})

if __name__ == '__main__':
    app.run()

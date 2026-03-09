import os, json
from typing import Any, Dict, List
from flask import Flask, Response, request
from flask.json import jsonify


app = Flask(__name__)

def load_customer_data():
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'customers.json')
    
    with open(file_path, 'r') as f:
        return json.load(f)

ALL_CUSTOMERS: List[Dict[str, Any]] = load_customer_data()
TOTAL_CUSTOMERS: int = len(ALL_CUSTOMERS)

@app.route("/api/health", methods=["GET"])
def health_check() -> tuple[Response, int]:
    return jsonify({
        "status": "healthy"
    }), 200

@app.route("/api/customers", methods=["GET"])
def get_customers() -> tuple[Response, int]:
    try:
        page: int = int(request.args.get('page', 1))
        limit: int = int(request.args.get('limit', 10))

        start_index: int = (page - 1) * limit
        end_index: int = start_index + limit

        paginated_data = ALL_CUSTOMERS[start_index:end_index]

        return jsonify({
            "data": paginated_data,
            "total": TOTAL_CUSTOMERS,
            "page": page,
            "limmit": limit
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route("/api/customers/<string:customer_id>", methods=["GET"])
def get_customer_by_id(customer_id) -> tuple[Response, int]:
    try:
        customer = next((c for c in ALL_CUSTOMERS if c["customer_id"] == customer_id), None)
        
        if customer is None:
            return jsonify({
                "error": "Customer not found"
            }), 404
            
        return jsonify({
            "data": customer
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

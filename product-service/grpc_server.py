
from concurrent import futures
from decimal import Decimal
import sys
from pathlib import Path

import grpc

# Make the app folder importable
sys.path.insert(0, str(Path(__file__).parent / "app"))

import product_pb2
import product_pb2_grpc

import models
from database import SessionLocal


class ProductService(product_pb2_grpc.ProductServiceServicer):

    def GetProduct(self, request, context):
        db = SessionLocal()

        try:
            product = db.get(models.Product, request.product_id)

            if product is None or not product.is_active:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Product not found",
                )

            return product_pb2.ProductResponse(
                id=product.id,
                name=product.name,
                description=product.description or "",
                price=str(Decimal(product.price)),
                image_url=product.image_url or "",
                is_active=product.is_active,
            )

        finally:
            db.close()


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    product_pb2_grpc.add_ProductServiceServicer_to_server(
        ProductService(),
        server,
    )

    server.add_insecure_port("[::]:50052")
    server.start()

    print("Product gRPC server running on port 50052")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve()
